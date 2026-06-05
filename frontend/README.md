# AI Cost Detective Frontend

This is the Next.js frontend for the AI Cost Detective FinOps platform.

## Features

- **Next.js 16 (App Router)** with React 18+ and Turbopack
- **Authentication**: Azure Entra ID integrated via NextAuth v5
- **Data Fetching**: Fully integrated with the backend FastAPI endpoints using TanStack Query
- **Styling**: Tailwind CSS v4, `oklch`-based dynamic dark-mode palette
- **Components**: `shadcn/ui` foundation (Radix / Base UI)
- **Visualizations**: Interactive charts and data tables built with `Recharts`
- **Real-Time Data**: WebSocket connection directly to backend analysis queues for live status updates
- **Animations**: `framer-motion` page transitions and element entry effects

## Setup

First, run the development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment Variables

Create a `.env.local` file with the following configurations:

```env
AUTH_SECRET="your-nextauth-secret-string"
AUTH_AZURE_AD_CLIENT_ID="your-azure-ad-client-id"
AUTH_AZURE_AD_CLIENT_SECRET="your-azure-ad-client-secret"
AUTH_AZURE_AD_TENANT_ID="your-azure-ad-tenant-id"

# Backend API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
NEXT_PUBLIC_WS_URL="ws://localhost:8000"
```
