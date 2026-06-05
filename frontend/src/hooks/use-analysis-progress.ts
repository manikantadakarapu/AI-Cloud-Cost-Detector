import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import type { ProgressMessage } from "@/types/api"

export function useAnalysisProgress(analysisId: string) {
  const { data: session } = useSession()
  const [progress, setProgress] = useState<ProgressMessage | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!session?.tenantId || !analysisId) return

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
    const ws = new WebSocket(`${wsUrl}/ws/analysis/${analysisId}?tenant_id=${session.tenantId}`)

    ws.onopen = () => setIsConnected(true)
    
    ws.onmessage = (event) => {
      try {
        const data: ProgressMessage = JSON.parse(event.data)
        setProgress(data)
      } catch (err) {
        console.error("Failed to parse WebSocket message", err)
      }
    }

    ws.onclose = () => setIsConnected(false)

    return () => {
      ws.close()
    }
  }, [analysisId, session?.tenantId])

  return { progress, isConnected }
}
