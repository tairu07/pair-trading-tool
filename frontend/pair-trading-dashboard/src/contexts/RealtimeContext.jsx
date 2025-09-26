import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'

// WebSocket URL
const WS_URL = 'ws://localhost:8000/ws'

// Initial state
const initialState = {
  pairs: {},
  alerts: [],
  prices: {},
  systemStatus: {
    monitoring: false,
    connections: 0
  }
}

// Action types
const ActionTypes = {
  UPDATE_PAIR: 'UPDATE_PAIR',
  ADD_ALERT: 'ADD_ALERT',
  UPDATE_PRICE: 'UPDATE_PRICE',
  UPDATE_SYSTEM_STATUS: 'UPDATE_SYSTEM_STATUS',
  CLEAR_ALERTS: 'CLEAR_ALERTS'
}

// Reducer
const realtimeReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.UPDATE_PAIR:
      return {
        ...state,
        pairs: {
          ...state.pairs,
          [action.payload.pair_id]: {
            ...state.pairs[action.payload.pair_id],
            ...action.payload
          }
        }
      }
      
    case ActionTypes.ADD_ALERT:
      return {
        ...state,
        alerts: [action.payload, ...state.alerts.slice(0, 49)] // Keep last 50 alerts
      }
      
    case ActionTypes.UPDATE_PRICE:
      return {
        ...state,
        prices: {
          ...state.prices,
          [action.payload.symbol]: action.payload
        }
      }
      
    case ActionTypes.UPDATE_SYSTEM_STATUS:
      return {
        ...state,
        systemStatus: {
          ...state.systemStatus,
          ...action.payload
        }
      }
      
    case ActionTypes.CLEAR_ALERTS:
      return {
        ...state,
        alerts: []
      }
      
    default:
      return state
  }
}

// Context
const RealtimeContext = createContext()

// Provider component
export const RealtimeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(realtimeReducer, initialState)
  const { isConnected, lastMessage, sendMessage, connectionError } = useWebSocket(WS_URL)

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage)
    }
  }, [lastMessage])

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'pair_update':
        dispatch({
          type: ActionTypes.UPDATE_PAIR,
          payload: message.data
        })
        break
        
      case 'alert':
        dispatch({
          type: ActionTypes.ADD_ALERT,
          payload: {
            ...message.data,
            id: Date.now(), // Temporary ID for frontend
            timestamp: new Date(message.data.timestamp)
          }
        })
        
        // Show browser notification if supported
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification(`Pair Trading Alert: ${message.data.type}`, {
            body: message.data.message,
            icon: '/favicon.ico'
          })
        }
        break
        
      case 'price_update':
        dispatch({
          type: ActionTypes.UPDATE_PRICE,
          payload: message.data
        })
        break
        
      case 'system_status':
        dispatch({
          type: ActionTypes.UPDATE_SYSTEM_STATUS,
          payload: message.data
        })
        break
        
      case 'pong':
        // Handle ping/pong for connection health
        break
        
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  // Actions
  const actions = {
    startMonitoring: () => {
      sendMessage({ type: 'start_monitoring' })
    },
    
    stopMonitoring: () => {
      sendMessage({ type: 'stop_monitoring' })
    },
    
    subscribeToPair: (pairId) => {
      sendMessage({ type: 'subscribe_pair', pair_id: pairId })
    },
    
    clearAlerts: () => {
      dispatch({ type: ActionTypes.CLEAR_ALERTS })
    },
    
    requestNotificationPermission: async () => {
      if ('Notification' in window && Notification.permission === 'default') {
        const permission = await Notification.requestPermission()
        return permission === 'granted'
      }
      return Notification.permission === 'granted'
    }
  }

  const value = {
    ...state,
    isConnected,
    connectionError,
    actions
  }

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  )
}

// Hook to use the context
export const useRealtime = () => {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider')
  }
  return context
}

export default RealtimeContext
