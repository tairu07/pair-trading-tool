"""
J-Quants API Client for fetching market data
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Price data structure"""
    date: str
    code: str
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[float]
    adjustment_close: Optional[float]


class JQuantsClient:
    """J-Quants API Client"""
    
    BASE_URL = "https://api.jquants.com/v1"
    
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self.id_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._ensure_valid_token()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid ID token"""
        if (self.id_token is None or 
            self.token_expires_at is None or 
            datetime.now() >= self.token_expires_at - timedelta(minutes=5)):
            await self._refresh_id_token()
    
    async def _refresh_id_token(self):
        """Refresh ID token using refresh token"""
        url = f"{self.BASE_URL}/token/auth_refresh"
        params = {"refreshtoken": self.refresh_token}
        
        try:
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.id_token = data["idToken"]
                    # ID token expires in 24 hours
                    self.token_expires_at = datetime.now() + timedelta(hours=23)
                    logger.info("Successfully refreshed ID token")
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to refresh token: {response.status} - {error_text}")
                    raise Exception(f"Failed to refresh token: {response.status}")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to J-Quants API"""
        await self._ensure_valid_token()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {self.id_token}"}
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_text}")
                    raise Exception(f"API request failed: {response.status}")
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            raise
    
    async def get_listed_info(self) -> List[Dict[str, Any]]:
        """Get list of all listed companies"""
        try:
            data = await self._make_request("/listed/info")
            return data.get("info", [])
        except Exception as e:
            logger.error(f"Error fetching listed info: {e}")
            return []
    
    async def get_daily_quotes(
        self, 
        code: Optional[str] = None,
        date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[PriceData]:
        """
        Get daily price quotes
        
        Args:
            code: Stock code (e.g., "7203")
            date: Specific date (YYYY-MM-DD or YYYYMMDD)
            from_date: Start date for range query
            to_date: End date for range query
        """
        params = {}
        
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        try:
            data = await self._make_request("/prices/daily_quotes", params)
            quotes = data.get("daily_quotes", [])
            
            price_data = []
            for quote in quotes:
                price_data.append(PriceData(
                    date=quote.get("Date"),
                    code=quote.get("Code"),
                    open=quote.get("Open"),
                    high=quote.get("High"),
                    low=quote.get("Low"),
                    close=quote.get("Close"),
                    volume=quote.get("Volume"),
                    adjustment_close=quote.get("AdjustmentClose")
                ))
            
            return price_data
        except Exception as e:
            logger.error(f"Error fetching daily quotes: {e}")
            return []
    
    async def get_price_history(
        self, 
        symbol: str, 
        days: int = 200
    ) -> List[PriceData]:
        """
        Get price history for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to fetch (default: 200)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 50)  # Add buffer for weekends/holidays
        
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        return await self.get_daily_quotes(
            code=symbol,
            from_date=from_date,
            to_date=to_date
        )
    
    async def get_multiple_symbols_data(
        self, 
        symbols: List[str], 
        date: str
    ) -> Dict[str, PriceData]:
        """
        Get price data for multiple symbols on a specific date
        
        Args:
            symbols: List of stock symbols
            date: Date in YYYY-MM-DD format
        """
        result = {}
        
        # J-Quants allows fetching all symbols for a specific date
        all_quotes = await self.get_daily_quotes(date=date)
        
        # Filter for requested symbols
        for quote in all_quotes:
            if quote.code in symbols:
                result[quote.code] = quote
        
        return result


# Utility functions for data processing
def calculate_returns(prices: List[PriceData]) -> List[float]:
    """Calculate daily returns from price data"""
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1].adjustment_close and prices[i].adjustment_close:
            ret = (prices[i].adjustment_close - prices[i-1].adjustment_close) / prices[i-1].adjustment_close
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns


def align_price_series(prices_a: List[PriceData], prices_b: List[PriceData]) -> tuple:
    """
    Align two price series by date
    
    Returns:
        Tuple of (aligned_prices_a, aligned_prices_b)
    """
    # Create dictionaries for fast lookup
    dict_a = {p.date: p for p in prices_a if p.date and p.adjustment_close}
    dict_b = {p.date: p for p in prices_b if p.date and p.adjustment_close}
    
    # Find common dates
    common_dates = sorted(set(dict_a.keys()) & set(dict_b.keys()))
    
    aligned_a = [dict_a[date] for date in common_dates]
    aligned_b = [dict_b[date] for date in common_dates]
    
    return aligned_a, aligned_b


# Example usage and testing
async def test_jquants_client():
    """Test function for J-Quants client"""
    refresh_token = os.getenv("J_QUANTS_REFRESH_TOKEN")
    if not refresh_token:
        print("Please set J_QUANTS_REFRESH_TOKEN environment variable")
        return
    
    async with JQuantsClient(refresh_token) as client:
        # Test getting listed companies
        print("Fetching listed companies...")
        companies = await client.get_listed_info()
        print(f"Found {len(companies)} companies")
        
        # Test getting price data for Toyota
        print("\nFetching Toyota (7203) price data...")
        toyota_prices = await client.get_price_history("7203", days=30)
        print(f"Found {len(toyota_prices)} price records for Toyota")
        
        if toyota_prices:
            latest = toyota_prices[-1]
            print(f"Latest price: {latest.date} - Close: {latest.adjustment_close}")


if __name__ == "__main__":
    asyncio.run(test_jquants_client())
