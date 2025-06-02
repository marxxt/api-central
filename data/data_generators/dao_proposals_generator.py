import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from pydantic import BaseModel
from faker import Faker
from db_utils import supabase_bot  # Ensure this points to your Supabase adapter
import httpx

fake = Faker()

# --- Vote Model ---
class Vote(BaseModel):
    user_id: str
    vote: str  # 'yes', 'no', or 'abstain'
    voted_at: datetime

# --- Proposal Model ---
class Proposal(BaseModel):
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    passed: bool
    value: float
    dao: str

def generate_fake_proposals(dao_ids: List[List[str]], user_ids: List[str], num_proposals_per_dao: int = 2) -> Tuple[List[Proposal], List[dict]]:
    proposals = []
    votes = []

    for dao_id in dao_ids:
        for _ in range(num_proposals_per_dao):
            proposal_id = str(uuid.uuid4())
            start = fake.date_time_between(start_date="-30d", end_date="-5d", tzinfo=timezone.utc)
            end = start + timedelta(days=random.randint(1, 7))
            proposal = Proposal(
                id=proposal_id,
                name=fake.sentence(nb_words=4),
                description=fake.paragraph(),
                start_date=start,
                end_date=end,
                passed=random.choice([True, False]),
                value=round(random.uniform(1000, 100000), 2),
                dao=dao_id[0],
            )
            proposals.append(proposal)

            vote_count = random.randint(1, 5)
            for _ in range(vote_count):
                vote = Vote(
                    user_id=random.choice(user_ids), # Select user_id from existing user_ids
                    vote=random.choice(["yes", "no", "abstain"]),
                    voted_at=fake.date_time_between(start_date=start, end_date=end, tzinfo=timezone.utc)
                )
                votes.append({
                    "proposal_id": proposal_id,
                    "user_id": vote.user_id,
                    "vote": vote.vote,
                    "voted_at": vote.voted_at.isoformat()
                })

    return proposals, votes

def insert_fake_proposals(proposals: List[Proposal], votes: List[dict]):
    for proposal in proposals:
        try:
            data = proposal.model_dump()
            data["start_date"] = data["start_date"].isoformat()
            data["end_date"] = data["end_date"].isoformat()
            supabase_bot.table("dao_proposals").insert(data).execute()
            print(f"✅ Inserted proposal: {proposal.name} for DAO {proposal.dao}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"❌ Error inserting proposal for DAO {proposal.dao}: Table 'dao_proposals' not found or inaccessible. Please ensure the table exists and has correct permissions. Original error: {e}")
            else:
                print(f"❌ HTTP error inserting proposal for DAO {proposal.dao}: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred inserting proposal for DAO {proposal.dao}: {e}")

    for vote in votes:
        try:
            supabase_bot.table("dao_votes").insert(vote).execute()
            print(f"✅ Inserted vote by user {vote['user_id']} for proposal {vote['proposal_id']}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"❌ Error inserting vote for proposal {vote['proposal_id']}: Table 'dao_votes' not found or inaccessible. Please ensure the table exists and has correct permissions. Original error: {e}")
            else:
                print(f"❌ HTTP error inserting vote for proposal {vote['proposal_id']}: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred inserting vote for proposal {vote['proposal_id']}: {e}")

if __name__ == "__main__":
    dummy_dao_ids = [[str(uuid.uuid4()) for _ in range(3)]]
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(5)] # Create some dummy user IDs for local testing
    proposals, votes = generate_fake_proposals(dummy_dao_ids, dummy_user_ids)
    insert_fake_proposals(proposals, votes)
