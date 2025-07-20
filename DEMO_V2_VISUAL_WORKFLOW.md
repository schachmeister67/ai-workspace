# Demo_v2.py - Visual Workflow Diagram

## 📊 **ASCII Flow Diagram**

```
┌─────────────────┐
│   User Input    │
│ "Show actors"   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│   demo_v2.py    │
│ Streamlit UI    │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ai_sql_agent_v2  │
│ SQL Generation  │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│sql_execution_api│
│ Query Execution │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│   PostgreSQL    │
│    Database     │
└─────────┬───────┘
          │
          v (Raw Results)
┌─────────────────┐
│ Response        │
│ Processing      │
└─────────┬───────┘
          │
          v (Formatted Data)
┌─────────────────┐
│ Formatted       │
│ Tables          │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ Streamlit UI    │
│ Display Results │
└─────────────────┘
```

## 🔄 **Detailed Component Flow**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                USER INTERACTION                                 │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            STREAMLIT UI (demo_v2.py)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Result    │  │    JSON     │  │ SQL Statement│  │ ERD Diagram │          │
│  │     Tab     │  │    Tab      │  │     Tab     │  │     Tab     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │ process_query(user_input)
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AI SQL AGENT (ai_sql_agent_v2.py)                       │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ Natural Language│ →  │ DDL Enhanced    │ →  │ Gemini AI       │            │
│  │ Input Processing│    │ Prompt Creation │    │ SQL Generation  │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │ Generated SQL Query
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SQL EXECUTION API (sql_execution_api.py)                     │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ SQL Validation  │ →  │ Query Execution │ →  │ Result          │            │
│  │ & Preparation   │    │ & Error Handling│    │ Formatting      │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │ Database Query
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            PostgreSQL DATABASE                                 │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ DVD Rental      │    │ Tables:         │    │ Raw Data        │            │
│  │ Schema          │    │ actor, film,    │    │ Results         │            │
│  │                 │    │ rental, etc.    │    │                 │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │ Raw Results
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE PROCESSING                                     │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ Data Type       │ →  │ DataFrame       │ →  │ 1-Based Index   │            │
│  │ Detection       │    │ Conversion      │    │ & Clean Columns │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└───────────────────────────────┬─────────────────────────────────────────────────┘
                                │ Formatted Results
                                v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          FORMATTED DISPLAY                                     │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ Professional    │    │ Left-Aligned    │    │ User-Friendly   │            │
│  │ Tables          │    │ Columns         │    │ Interface       │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔀 **Data Flow Diagram**

```
INPUT STAGE:
┌──────────────────┐
│ "Show actors"    │ (Natural Language)
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ Text Processing  │
└─────────┬────────┘

GENERATION STAGE:
          │
          v
┌──────────────────┐
│ DDL Context +    │
│ Natural Language │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ Gemini AI        │ 
│ LLM Processing   │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ "SELECT * FROM   │ (Generated SQL)
│  actor LIMIT 5;" │
└─────────┬────────┘

EXECUTION STAGE:
          │
          v
┌──────────────────┐
│ SQL Validation   │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ Database Query   │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ [{"actor_id":1,  │ (Raw JSON Results)
│  "first_name":   │
│  "Penelope"}...] │
└─────────┬────────┘

FORMATTING STAGE:
          │
          v
┌──────────────────┐
│ DataFrame        │
│ Conversion       │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ Column Cleanup   │
│ "first_name" →   │
│ "First Name"     │
└─────────┬────────┘
          │
          v
┌──────────────────┐
│ 1-Based Indexing │
│ [1,2,3,4,5]      │
└─────────┬────────┘

DISPLAY STAGE:
          │
          v
┌──────────────────┐
│ Formatted Table  │
│ ┌─────┬─────────┐│
│ │  1  │Penelope ││ (Professional Display)
│ │  2  │  Nick   ││
│ └─────┴─────────┘│
└──────────────────┘
```

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND LAYER                                   │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                              Streamlit UI                                   │ │
│ │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────┐  │ │
│ │  │ Input   │ │ Result  │ │  JSON   │ │   SQL   │ │   ERD Diagram       │  │ │
│ │  │ Field   │ │  Tab    │ │  Tab    │ │   Tab   │ │      Tab            │  │ │
│ │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────────┘  │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │ HTTP/Function Calls
                  v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PROCESSING LAYER                                  │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                          AI SQL Agent v2                                   │ │
│ │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐   │ │
│ │  │ NL to SQL   │ │ DDL Context  │ │ Gemini AI    │ │ Response        │   │ │
│ │  │ Processing  │ │ Enhancement  │ │ Integration  │ │ Assembly        │   │ │
│ │  └─────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘   │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │ HTTP API Calls
                  v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXECUTION LAYER                                   │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                        SQL Execution API                                    │ │
│ │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐   │ │
│ │  │ SQL         │ │ Query        │ │ Error        │ │ Result          │   │ │
│ │  │ Validation  │ │ Execution    │ │ Handling     │ │ Formatting      │   │ │
│ │  └─────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘   │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │ SQL Queries
                  v
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                DATA LAYER                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                            PostgreSQL Database                              │ │
│ │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐   │ │
│ │  │ DVD Rental  │ │ Tables       │ │ Indexes      │ │ Constraints     │   │ │
│ │  │ Schema      │ │ & Relations  │ │ & Keys       │ │ & Triggers      │   │ │
│ │  └─────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘   │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📈 **Performance & Error Flow**

```
SUCCESS PATH:
User Input → AI Processing → SQL Generation → Database Query → Results → Display
    ↓             ↓              ↓               ↓              ↓         ↓
   Fast         ~2-3s          ~100ms           ~50ms         ~10ms    Instant

ERROR HANDLING PATHS:

API Unavailable:
User Input → AI Agent → ❌ API Check → Error Message → Display Error

SQL Generation Error:
User Input → AI Agent → ❌ Invalid SQL → Error Response → Display Error

Database Error:
User Input → AI Agent → SQL → ❌ DB Query → Error Handling → Display Error

Formatting Error:
User Input → AI Agent → SQL → DB Results → ❌ Format → Fallback Format
```

This visual representation shows the complete flow from user input through the various processing stages to the final formatted display in the Streamlit UI.

## 🎯 **Key Flow Points**

1. **Input**: Natural language query from user
2. **Processing**: AI-powered SQL generation with DDL context
3. **Execution**: Secure SQL execution via dedicated API
4. **Formatting**: Professional table formatting with 1-based indexing
5. **Display**: Multi-tab view with results, JSON, SQL, and ERD

The modular architecture ensures clean separation of concerns and robust error handling at each stage.
