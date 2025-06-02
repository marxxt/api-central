from datetime import datetime, timedelta, timezone
import json
import uuid
import random
from typing import List, Tuple, Union
from decimal import Decimal
from faker import Faker
from pydantic import BaseModel, Field
from db_utils import supabase_bot

fake = Faker()

# --- Pydantic Models ---

class OHLCModel(BaseModel):
    pair_id: str
    time: datetime
    open: str
    high: str
    low: str
    close: str

class VolumeModel(BaseModel):
    pair_id: str
    time: datetime
    value: str
    color: str

class TradingPairModel(BaseModel):
    pairs: str
    base_asset_id: str
    base_asset_symbol: str
    quote_asset_symbol: str
    last_price: str
    price_change_24h_percent: str
    high_24h: str
    low_24h: str
    volume_24h_base: str
    volume_24h_quote: str
    is_favorite: bool
    order_book_id: str

class TradingPairReturn(BaseModel):
    trading_pair_model: TradingPairModel
    temp_trading_pair_uuid: str

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)
    
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
    
# --- Generator Functions ---

def generate_trading_pair_and_history(property_ids: List[List[str]], num_pairs_per_property: int = 1):
    trading_pairs: List[TradingPairReturn] = []
    ohlc_rows = []
    volume_rows = []

    quote_assets = ["USDC", "ETH", "USDT", "BELLS"]
    num_days = random.randint(60, 90)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=num_days)

    for prop in property_ids:
        for _ in range(num_pairs_per_property):
            base_symbol = fake.unique.lexify(text="???").upper()
            quote_symbol = random.choice(quote_assets)
            pair_name = f"{base_symbol}_{quote_symbol}"
            temp_trading_pair_uuid = str(uuid.uuid4())
            current_price = Decimal(str(round(random.uniform(10, 100), 2)))

            for i in range(num_days):
                date = start_date + timedelta(days=i)
                timestamp = date.replace(hour=0, minute=0, second=0, microsecond=0)

                open_price = current_price
                high_price = open_price * Decimal(str(random.uniform(1.01, 1.05)))
                low_price = open_price * Decimal(str(random.uniform(0.95, 0.99)))
                close_price = Decimal(str(random.uniform(float(low_price), float(high_price))))
                volume = Decimal(str(round(random.uniform(1000, 10000), 2)))
                color = "rgba(0, 150, 136, 1)" if close_price >= open_price else "rgba(255, 82, 82, 1)"

                ohlc_rows.append(OHLCModel(
                    pair_id=temp_trading_pair_uuid,
                    time=timestamp,
                    open=str(open_price),
                    high=str(high_price),
                    low=str(low_price),
                    close=str(close_price)
                ))

                volume_rows.append(VolumeModel(
                    pair_id=temp_trading_pair_uuid,
                    time=timestamp,
                    value=str(volume),
                    color=color
                ))

                current_price = close_price

            model = TradingPairModel(
                    pairs=pair_name,
                    base_asset_id=prop[0],
                    base_asset_symbol=base_symbol,
                    quote_asset_symbol=quote_symbol,
                    last_price=json.dumps(current_price, cls=JSONEncoder),
                    price_change_24h_percent=json.dumps(round(random.uniform(-10, 10), 2), cls=JSONEncoder),
                    high_24h=json.dumps(current_price * Decimal('1.05'), cls=JSONEncoder),
                    low_24h=json.dumps(current_price * Decimal('0.95'), cls=JSONEncoder),
                    volume_24h_base=json.dumps(Decimal(str(round(random.uniform(10000, 1000000), 2))), cls=JSONEncoder),
                    volume_24h_quote=json.dumps(Decimal(str(round(random.uniform(5000, 500000), 2))), cls=JSONEncoder),
                    is_favorite=fake.boolean(),
                    order_book_id=str(uuid.uuid4())
                )
            trade_pair_return = TradingPairReturn(trading_pair_model=model, temp_trading_pair_uuid=temp_trading_pair_uuid)
            trading_pairs.append(trade_pair_return)

    return trading_pairs, ohlc_rows, volume_rows

# --- Insertion Functions ---

def insert_all_trading_data(pairs_with_temp_uuids: List[TradingPairReturn], ohlcs: List[OHLCModel], volumes: List[VolumeModel]):
    inserted_ids = []
    temp_to_supabase_id_map = {}

    for pair_entry in pairs_with_temp_uuids:
        pair_model = pair_entry.trading_pair_model
        temp_uuid = pair_entry.temp_trading_pair_uuid
        try:
            pair_data = pair_model.model_dump()
            # print("pair_data",pair_data)
            for key in ['last_price', 'price_change_24h_percent', 'high_24h', 'low_24h', 'volume_24h_base', 'volume_24h_quote']:
                pair_data[key] = float(pair_data[key])
            # print("PAIR_DATA",pair_data)
            response = supabase_bot.table("trading_pairs").upsert(pair_model.model_dump()).execute()
            # print("we did not make it here")
            inserted = response.data[0]
            supabase_id = inserted["id"]
            inserted_ids.append(supabase_id)
            temp_to_supabase_id_map[temp_uuid] = supabase_id
            print(f"✅ Inserted pair {pair_model.pairs} with ID: {supabase_id}")
        except Exception as e:
            print(f"❌ Error inserting pair {pair_model.pairs}: {e}")

    for row in ohlcs:
        row.pair_id = temp_to_supabase_id_map.get(row.pair_id, row.pair_id)
        try:
            ohlc_dict = row.model_dump(exclude_none=True)
            # print("ohlc_dict", ohlc_dict)
            ohlc_dict["time"] = ohlc_dict["time"].isoformat()
            ohlc_dict["open"] = float(ohlc_dict["open"])
            ohlc_dict["high"] = float(ohlc_dict["high"])
            ohlc_dict["low"] = float(ohlc_dict["low"])
            ohlc_dict["close"] = float(ohlc_dict["close"])
            supabase_bot.table("ohlc_data").insert(ohlc_dict).execute()
            # print("ohlc_dict",ohlc_dict)

        except Exception as e:
            print(f"❌ Error inserting OHLC row: {e}")

    for row in volumes:
        row.pair_id = temp_to_supabase_id_map.get(row.pair_id, row.pair_id)
        try:
            volume_dict = row.model_dump(exclude_none=True)
            volume_dict["time"] = volume_dict["time"].isoformat()
            volume_dict["value"] = float(volume_dict["value"])
            supabase_bot.table("volume_data").insert(volume_dict).execute()
            # print("volume_dict",volume_dict)
        except Exception as e:
            print(f"❌ Error inserting volume row: {e}")

    return inserted_ids

# --- Main Execution ---

if __name__ == "__main__":
    dummy_properties = [[str(uuid.uuid4()), str(uuid.uuid4())] for _ in range(3)]
    pairs_with_temp_uuids, ohlcs, volumes = generate_trading_pair_and_history(dummy_properties)
    insert_all_trading_data(pairs_with_temp_uuids, ohlcs, volumes)
