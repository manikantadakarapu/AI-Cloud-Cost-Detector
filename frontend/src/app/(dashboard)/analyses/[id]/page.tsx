"use client"

import { use } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  AlertTriangle,
  Server,
  DollarSign,
  ShieldAlert,
  Gauge
} from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts"

import { useAnalysisProgress } from "@/hooks/use-analysis-progress"
import { 
  useAnalysisStatus, 
  useAnalysisFindings, 
  useAnalysisCostSummary, 
  useAnalysisScore 
} from "@/lib/queries"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const STAGES = [
  { id: "queued", label: "Queued" },
  { id: "resource-discovery", label: "Resource Discovery" },
  { id: "cost-analysis", label: "Cost Analysis" },
  { id: "advisor-analysis", label: "Advisor Recommendations" },
  { id: "metrics-analysis", label: "Metrics Analysis" },
  { id: "finops-analysis", label: "FinOps Evaluation" },
  { id: "scoring", label: "Generating Score" },
  { id: "completed", label: "Completed" }
]

export default function AnalysisDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const id = resolvedParams.id
  
  // Real-time WebSocket updates
  const { progress: wsProgress, isConnected } = useAnalysisProgress(id)
  
  // Polling fallback
  const { data: pollData } = useAnalysisStatus(id)

  const status = wsProgress?.status || pollData?.status || "queued"
  const currentStage = wsProgress?.stage || pollData?.current_stage || "queued"
  const progressPercentage = wsProgress?.progress ?? pollData?.progress_percentage ?? 0
  const errorMessage = wsProgress?.error || pollData?.error_message

  const isCompleted = status === "completed"
  const isFailed = status === "failed"

  // Fetch results only if completed
  const { data: findings } = useAnalysisFindings(id, isCompleted)
  const { data: costSummary } = useAnalysisCostSummary(id, isCompleted)
  const { data: score } = useAnalysisScore(id, isCompleted)

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Analysis Report</h2>
          <p className="text-muted-foreground flex items-center gap-2 mt-1">
            <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{id}</span>
            {!isConnected && status !== "completed" && status !== "failed" && (
              <Badge variant="outline" className="text-xs font-normal border-warning/50 text-warning">
                Polling fallback active (WebSocket disconnected)
              </Badge>
            )}
          </p>
        </div>
        <Badge 
          variant={isCompleted ? "default" : isFailed ? "destructive" : "secondary"}
          className={`text-sm px-3 py-1 ${isCompleted ? 'bg-success hover:bg-success/80 text-success-foreground' : ''}`}
        >
          {status.toUpperCase()}
        </Badge>
      </div>

      {!isCompleted && !isFailed ? (
        <Card className="glass border-primary/20 shadow-lg shadow-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              Analysis in Progress
            </CardTitle>
            <CardDescription>Discovering resources and evaluating FinOps rules...</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="font-medium text-primary capitalize">{currentStage?.replace('-', ' ')}</span>
                <span className="font-mono">{progressPercentage}%</span>
              </div>
              <Progress value={progressPercentage} className="h-2 bg-muted/50" />
            </div>

            <div className="relative pt-4">
              <div className="absolute left-[15px] top-4 bottom-0 w-px bg-border z-0" />
              <div className="space-y-6 relative z-10">
                {STAGES.map((stage, i) => {
                  const stageIndex = STAGES.findIndex(s => s.id === currentStage)
                  const isCurrent = stage.id === currentStage || (currentStage === "queued" && i === 0)
                  const isPast = isCompleted || (stageIndex > -1 && i < stageIndex)
                  
                  return (
                    <motion.div 
                      key={stage.id} 
                      className={`flex items-center gap-4 ${isPast || isCurrent ? "opacity-100" : "opacity-40"}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: isPast || isCurrent ? 1 : 0.4, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-colors duration-500
                        ${isPast ? "bg-primary border-primary text-primary-foreground" : 
                          isCurrent ? "bg-background border-primary text-primary shadow-[0_0_10px_rgba(var(--color-primary),0.5)]" : 
                          "bg-background border-border text-muted-foreground"}`}
                      >
                        {isPast ? <CheckCircle2 className="w-4 h-4" /> : <div className={`w-2 h-2 rounded-full ${isCurrent ? "bg-primary animate-pulse" : "bg-muted-foreground"}`} />}
                      </div>
                      <div className="flex flex-col">
                        <span className={`text-sm font-medium ${isCurrent ? "text-primary" : ""}`}>{stage.label}</span>
                        {isCurrent && <span className="text-xs text-muted-foreground">Running...</span>}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      ) : isFailed ? (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <XCircle className="w-5 h-5" /> Analysis Failed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-destructive/80 font-mono bg-destructive/10 p-4 rounded-md border border-destructive/20">
              {errorMessage || "An unknown error occurred during the analysis pipeline."}
            </p>
          </CardContent>
        </Card>
      ) : (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-4 glass bg-muted/50 p-1">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="findings">Findings ({findings?.length || 0})</TabsTrigger>
              <TabsTrigger value="cost">Cost Details</TabsTrigger>
              <TabsTrigger value="score">FinOps Score</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-3">
                <Card className="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2"><Gauge className="w-4 h-4 text-info"/> FinOps Score</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{score?.overall_score ?? "---"}<span className="text-base text-muted-foreground font-normal">/100</span></div>
                  </CardContent>
                </Card>
                <Card className="glass border-success/20">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2 text-success"><DollarSign className="w-4 h-4"/> Potential Savings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-success">{costSummary ? formatCurrency(costSummary.potential_savings) : "---"}</div>
                  </CardContent>
                </Card>
                <Card className="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2"><Server className="w-4 h-4 text-primary"/> Resources Scanned</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{costSummary?.resource_count ?? "---"}</div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="findings" className="mt-6">
              <Card className="glass">
                <CardHeader>
                  <CardTitle>Optimization Findings</CardTitle>
                  <CardDescription>Actionable recommendations based on FinOps principles.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border border-border">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-muted/50 border-b border-border">
                        <tr>
                          <th className="p-4 font-medium text-muted-foreground w-24">Severity</th>
                          <th className="p-4 font-medium text-muted-foreground w-32">Category</th>
                          <th className="p-4 font-medium text-muted-foreground">Title</th>
                          <th className="p-4 font-medium text-muted-foreground text-right">Savings</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {findings?.map((f) => (
                          <tr key={f.id} className="hover:bg-muted/30">
                            <td className="p-4">
                              <Badge variant="outline" className={
                                f.severity === 'Critical' ? 'border-destructive text-destructive' :
                                f.severity === 'High' ? 'border-warning text-warning' :
                                f.severity === 'Medium' ? 'border-chart-2 text-chart-2' :
                                f.severity === 'Low' ? 'border-success text-success' : 'border-info text-info'
                              }>{f.severity}</Badge>
                            </td>
                            <td className="p-4 text-muted-foreground">{f.category}</td>
                            <td className="p-4 font-medium">{f.title}</td>
                            <td className="p-4 text-right text-success font-mono">{formatCurrency(f.estimated_monthly_savings)}</td>
                          </tr>
                        ))}
                        {(!findings || findings.length === 0) && (
                          <tr><td colSpan={4} className="p-8 text-center text-muted-foreground">No optimization findings discovered.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="cost" className="mt-6">
              <Card className="glass">
                <CardHeader>
                  <CardTitle>Cost Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold mb-2">{costSummary ? formatCurrency(costSummary.total_monthly_cost) : "---"}</div>
                  <p className="text-muted-foreground">Total monthly amortized cost across all scanned resources.</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="score" className="mt-6">
              <Card className="glass">
                <CardHeader>
                  <CardTitle>FinOps Assessment Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6 max-w-md">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-lg">Overall Score</span>
                      <span className="font-bold text-2xl text-primary">{score?.overall_score ?? 0}</span>
                    </div>
                    <Progress value={score?.overall_score ?? 0} className="h-3" />
                    
                    <div className="pt-4 space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">Compute</span>
                          <span>{score?.compute_score ?? 0}/100</span>
                        </div>
                        <Progress value={score?.compute_score ?? 0} className="h-1.5" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">Storage</span>
                          <span>{score?.storage_score ?? 0}/100</span>
                        </div>
                        <Progress value={score?.storage_score ?? 0} className="h-1.5" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">Network</span>
                          <span>{score?.network_score ?? 0}/100</span>
                        </div>
                        <Progress value={score?.network_score ?? 0} className="h-1.5" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      )}
    </div>
  )
}
