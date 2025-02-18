# Architecture Diagram (Mermaid)

```mermaid
graph TB
    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef database fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef ai fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    %% Frontend Components
    subgraph Frontend["Frontend (React)"]
        direction TB
        UI[React + TypeScript]
        MUI[Material-UI]
        RQ[React Query]
        Router[React Router]
        Axios[Axios Client]
        UI --> MUI
        UI --> RQ
        UI --> Router
        RQ --> Axios
    end

    %% Backend Components
    subgraph Backend["Backend (FastAPI)"]
        direction TB
        API[FastAPI]
        Auth[JWT Auth]
        BL[Business Logic]
        Models[Data Models]
        API --> Auth
        API --> BL
        BL --> Models
    end

    %% Database Components
    subgraph Database["Database (MongoDB)"]
        direction TB
        Mongo[MongoDB Atlas]
        GridFS[GridFS Storage]
        Collections[Collections]
        Indexes[Indexes]
        Mongo --> GridFS
        Mongo --> Collections
        Collections --> Indexes
    end

    %% AI Services Components
    subgraph AI["AI Services"]
        direction TB
        DeepInfra[DeepInfra API]
        Llama[Llama Model]
        Analysis[Resume Analysis]
        Skills[Skill Extraction]
        Scoring[Score Computation]
        DeepInfra --> Llama
        Llama --> Analysis
        Analysis --> Skills
        Analysis --> Scoring
    end

    %% Connections between components
    Axios --> API
    BL --> Mongo
    BL --> DeepInfra

    %% Apply styles
    class Frontend frontend
    class Backend backend
    class Database database
    class AI ai
```

You can use this diagram by:
1. Copying it into any markdown file
2. Viewing it on GitHub (which supports Mermaid natively)
3. Using Mermaid Live Editor (https://mermaid.live)
4. Using any markdown editor that supports Mermaid 