"""
Initialize sample data for development and testing
"""
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Symbol, Pair, AlertRule, TimeFrame
import uuid


def create_sample_symbols(db: Session):
    """Create sample symbols"""
    symbols_data = [
        # Toyota and Honda (automotive sector)
        {"symbol": "7203", "name": "トヨタ自動車", "exchange": "TSE", "sector": "自動車"},
        {"symbol": "7267", "name": "ホンダ", "exchange": "TSE", "sector": "自動車"},
        
        # Banks
        {"symbol": "8306", "name": "三菱UFJフィナンシャル・グループ", "exchange": "TSE", "sector": "銀行"},
        {"symbol": "8316", "name": "三井住友フィナンシャルグループ", "exchange": "TSE", "sector": "銀行"},
        
        # Technology
        {"symbol": "6758", "name": "ソニーグループ", "exchange": "TSE", "sector": "電気機器"},
        {"symbol": "6861", "name": "キーエンス", "exchange": "TSE", "sector": "電気機器"},
        
        # Retail
        {"symbol": "9983", "name": "ファーストリテイリング", "exchange": "TSE", "sector": "小売業"},
        {"symbol": "3382", "name": "セブン&アイ・ホールディングス", "exchange": "TSE", "sector": "小売業"},
    ]
    
    for symbol_data in symbols_data:
        existing = db.query(Symbol).filter(Symbol.symbol == symbol_data["symbol"]).first()
        if not existing:
            symbol = Symbol(**symbol_data)
            db.add(symbol)
    
    db.commit()
    print(f"Created {len(symbols_data)} sample symbols")


def create_sample_pairs(db: Session):
    """Create sample trading pairs"""
    pairs_data = [
        {
            "symbol_a": "7203",  # Toyota
            "symbol_b": "7267",  # Honda
            "name": "トヨタ/ホンダ ペア",
            "description": "自動車セクター内ペアトレード"
        },
        {
            "symbol_a": "8306",  # MUFG
            "symbol_b": "8316",  # SMFG
            "name": "MUFG/SMFG ペア",
            "description": "メガバンクペアトレード"
        },
        {
            "symbol_a": "6758",  # Sony
            "symbol_b": "6861",  # Keyence
            "name": "ソニー/キーエンス ペア",
            "description": "テクノロジーセクターペアトレード"
        },
        {
            "symbol_a": "9983",  # Fast Retailing
            "symbol_b": "3382",  # Seven & i
            "name": "ファーストリテイリング/セブン&アイ ペア",
            "description": "小売業セクターペアトレード"
        }
    ]
    
    created_pairs = []
    for pair_data in pairs_data:
        # Check if symbols exist
        symbol_a = db.query(Symbol).filter(Symbol.symbol == pair_data["symbol_a"]).first()
        symbol_b = db.query(Symbol).filter(Symbol.symbol == pair_data["symbol_b"]).first()
        
        if symbol_a and symbol_b:
            # Check if pair already exists
            existing = db.query(Pair).filter(
                Pair.symbol_a == pair_data["symbol_a"],
                Pair.symbol_b == pair_data["symbol_b"]
            ).first()
            
            if not existing:
                pair = Pair(**pair_data)
                db.add(pair)
                created_pairs.append(pair)
    
    db.commit()
    
    # Refresh to get the generated IDs
    for pair in created_pairs:
        db.refresh(pair)
    
    print(f"Created {len(created_pairs)} sample pairs")
    return created_pairs


def create_sample_alert_rules(db: Session, pairs):
    """Create sample alert rules for pairs"""
    for pair in pairs:
        # Entry rule for long position (z-score <= -2.0)
        entry_long_rule = AlertRule(
            pair_id=pair.pair_id,
            timeframe=TimeFrame.DAY_1,
            name=f"{pair.name} - Entry Long",
            description="Z-scoreが-2.0以下になったときのロングエントリーシグナル",
            params={
                "entry_z_threshold": -2.0,
                "alert_type": "entry_long",
                "cooldown_minutes": 60
            }
        )
        
        # Entry rule for short position (z-score >= 2.0)
        entry_short_rule = AlertRule(
            pair_id=pair.pair_id,
            timeframe=TimeFrame.DAY_1,
            name=f"{pair.name} - Entry Short",
            description="Z-scoreが2.0以上になったときのショートエントリーシグナル",
            params={
                "entry_z_threshold": 2.0,
                "alert_type": "entry_short",
                "cooldown_minutes": 60
            }
        )
        
        # Exit rule (z-score approaches 0)
        exit_rule = AlertRule(
            pair_id=pair.pair_id,
            timeframe=TimeFrame.DAY_1,
            name=f"{pair.name} - Exit",
            description="Z-scoreが0に近づいたときの利確シグナル",
            params={
                "exit_z_threshold": 0.2,
                "alert_type": "exit",
                "cooldown_minutes": 30
            }
        )
        
        db.add_all([entry_long_rule, entry_short_rule, exit_rule])
    
    db.commit()
    print(f"Created alert rules for {len(pairs)} pairs")


def main():
    """Initialize sample data"""
    print("Initializing sample data...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create sample data
        create_sample_symbols(db)
        pairs = create_sample_pairs(db)
        create_sample_alert_rules(db, pairs)
        
        print("Sample data initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
