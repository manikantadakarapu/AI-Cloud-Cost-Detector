"use client"

import { motion } from "framer-motion"
import { Gauge, Info } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"

import { useAnalyses, useAnalysisScore } from "@/lib/queries"

export default function FinOpsScorePage() {
  const { data: analyses, isLoading: analysesLoading } = useAnalyses()
  const latestAnalysis = analyses?.find(a => a.status === "completed")
  const latestId = latestAnalysis?.id || ""

  const { data: score, isLoading: scoreLoading } = useAnalysisScore(latestId, !!latestId)
  const isLoading = analysesLoading || scoreLoading

  const getScoreColor = (val: number) => {
    if (val >= 80) return "text-success"
    if (val >= 60) return "text-warning"
    return "text-destructive"
  }

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      <div className="flex flex-col gap-1 items-center text-center mb-8 mt-4">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-2">
          <Gauge className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight">FinOps Health Score</h2>
        <p className="text-muted-foreground max-w-lg">
          A standardized metric evaluating your cloud infrastructure against FinOps Foundation best practices.
        </p>
      </div>

      <Card className="glass relative overflow-hidden border-primary/20 shadow-lg shadow-primary/5">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-lg text-muted-foreground font-normal">Overall Assessment Score</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center pb-10">
          {isLoading ? (
            <Skeleton className="h-32 w-48 mt-4 mb-6" />
          ) : !latestId || !score ? (
            <div className="text-center text-muted-foreground flex flex-col items-center py-8">
              <Info className="w-8 h-8 mb-2 opacity-50" />
              <p>Run a FinOps analysis to calculate your score.</p>
            </div>
          ) : (
            <>
              <motion.div 
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", bounce: 0.5 }}
                className={`text-8xl font-black tracking-tighter ${getScoreColor(score.overall_score)} my-4`}
              >
                {score.overall_score}
              </motion.div>
              <div className="w-full max-w-md mt-4 relative">
                <Progress value={score.overall_score} className="h-4" />
                <div className="flex justify-between text-xs text-muted-foreground mt-2 font-mono">
                  <span>0 (Needs Work)</span>
                  <span>100 (Optimized)</span>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="glass">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compute Health</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-10 w-full" /> : (
              <div>
                <div className="text-2xl font-bold mb-2">{score?.compute_score ?? "---"}</div>
                <Progress value={score?.compute_score ?? 0} className="h-1.5" />
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Storage Health</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-10 w-full" /> : (
              <div>
                <div className="text-2xl font-bold mb-2">{score?.storage_score ?? "---"}</div>
                <Progress value={score?.storage_score ?? 0} className="h-1.5" />
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Network Health</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-10 w-full" /> : (
              <div>
                <div className="text-2xl font-bold mb-2">{score?.network_score ?? "---"}</div>
                <Progress value={score?.network_score ?? 0} className="h-1.5" />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
