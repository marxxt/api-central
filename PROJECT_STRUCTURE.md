universal-graphql-gateway/
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI + Strawberry entrypoint
│   ├── config.py                        # .env + PydanticSettings loader
│
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── middleware.py                # Supabase JWT middleware
│   │   └── utils.py                     # Token decode, role handling
│
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py                      # AbstractStorageAdapter
│   │   ├── supabase_adapter.py          # SQL backend
│   │   ├── redis_adapter.py             # Cache backend
│   │   └── firestore_adapter.py         # Firestore backend
│
│   ├── models/                          # Pydantic v2 models
│   │   ├── __init__.py
│   │   ├── auction.py                   # from auction.types.ts
│   │   ├── database.py                  # from database.types.ts
│   │   ├── enums.py                     # from enum.types.ts
│   │   ├── snft.py                      # from snft.types.ts
│   │   ├── trade.py                     # from trade.types.ts
│   │   ├── ui.py                        # from ui.types.ts
│   │   ├── user.py                      # from user.types.ts
│   │   └── index.py                     # mappings/index.ts if needed
│
│   ├── schema/                          # GraphQL schema
│   │   ├── __init__.py
│   │   ├── types/
│   │   │   ├── __init__.py
│   │   │   ├── user_type.py             # GraphQL type mappings from user models
│   │   │   ├── auction_type.py          # etc.
│   │   │   ├── snft_type.py
│   │   │   └── trade_type.py
│   │   └── resolvers/
│   │       ├── __init__.py
│   │       ├── user_resolver.py
│   │       ├── auction_resolver.py
│   │       ├── snft_resolver.py
│   │       └── trade_resolver.py
│
│   ├── services/                        # Business logic / aggregators
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── snft_service.py
│   │   └── trade_service.py
│
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py                # Custom errors
│       └── logger.py                    # Logging config
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_adapters/
│   │   ├── test_supabase.py
│   │   ├── test_firestore.py
│   │   └── test_redis.py
│   ├── test_models/
│   │   ├── test_user_model.py
│   │   ├── test_trade_model.py
│   │   └── ...
│   ├── test_schema/
│   │   ├── test_user_query.py
│   │   ├── test_snft_query.py
│   │   └── ...
│   └── test_services/
│       ├── test_user_service.py
│       └── ...
│
├── .env.example                         # Example config vars
├── Dockerfile                           # FastAPI + Poetry container
├── docker-compose.yml                   # Redis, Firebase emulator, etc.
├── README.md
├── PD.md                                # Project description
├── PLANNING.md                          # Project roadmap
├── pyproject.toml                       # Poetry-managed dependencies
└── .gitignore
