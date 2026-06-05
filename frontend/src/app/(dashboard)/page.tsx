"use client"

import { useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { useMutation } from "@tanstack/react-query"
import { motion, type Variants } from "framer-motion"
import {
  Activity,
  Database,
  Play,
  Loader2,
  DollarSign,
  ShieldAlert,
  TrendingDown,
  Gauge,
  BarChart4,
  Clock
} from "lucide-react"
import {
  Area,
  AreaChart,
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

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"

import api from "@/lib/api"
import {
  useAnalyses,
  useAnalysisCostSummary,
  useAnalysisFindings,
  useAnalysisScore,
  useResourceGroups,
  useSubscriptions,
  useTenantStats
} from "@/lib/queries"
import type { Analysis, Finding } from "@/types/api"

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
}

const itemVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
}

export default function DashboardPage() {
  const router = useRouter()
  const [selectedSub, setSelectedSub] = useState("")
  const [selectedRg, setSelectedRg] = useState("")

  // Global Tenant Data
  const { data: stats, isLoading: statsLoading } = useTenantStats()
  const { data: subscriptions, isLoading: subsLoading } = useSubscriptions()
  const { data: resourceGroups, isLoading: rgsLoading } = useResourceGroups(selectedSub)
  const { data: analyses, isLoading: analysesLoading } = useAnalyses()

  // Latest Analysis Data for KPI highlights
  const latestAnalysis = analyses && analyses.length > 0 ? analyses[0] : null
  const latestId = latestAnalysis?.id || ""

  const { data: costSummary, isLoading: costLoading } = useAnalysisCostSummary(latestId, !!latestId && latestAnalysis?.status === "completed")
  const { data: score, isLoading: scoreLoading } = useAnalysisScore(latestId, !!latestId && latestAnalysis?.status === "completed")
  const { data: findings, isLoading: findingsLoading } = useAnalysisFindings(latestId, !!latestId && latestAnalysis?.status === "completed")

  // Create Analysis Mutation
  const createAnalysis = useMutation({
    mutationFn: async () => {
      const res = await api.post("/analysis", {
        subscription_id: selectedSub,
        resource_group: selectedRg || "all", // backend fallback
      })
      return res.data
    },
    onSuccess: (data) => {
      router.push(`/analyses/${data.analysis_id}`)
    },
  })

  // Chart Data Processing
  const severityColors: Record<string, string> = {
    Critical: "var(--color-destructive)",
    High: "var(--color-warning)",
    Medium: "var(--color-chart-2)",
    Low: "var(--color-success)",
    Info: "var(--color-info)"
  }

  const findingsBySeverity = useMemo(() => findings?.reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>), [findings])

  const pieData = useMemo(() => findingsBySeverity
    ? Object.entries(findingsBySeverity).map(([name, value]) => ({ name, value }))
    : [], [findingsBySeverity])

  const topSavings = useMemo(() => findings
    ? [...findings].sort((a, b) => b.estimated_monthly_savings - a.estimated_monthly_savings).slice(0, 5)
    : [], [findings])

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <motion.div 
      className="space-y-6 pb-12"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants} className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h2>
        <p className="text-muted-foreground">Overview of your Azure FinOps landscape and cost optimization opportunities.</p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <motion.div variants={itemVariants}>
          <Card className="glass h-full relative overflow-hidden group hover:border-primary/50 transition-colors">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Resources Scanned</CardTitle>
              <Database className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? <Skeleton className="h-8 w-16" /> : (stats?.resource_count || 0).toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Tenant-wide visibility</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass h-full relative overflow-hidden group hover:border-primary/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Monthly Cost</CardTitle>
              <DollarSign className="h-4 w-4 text-chart-2" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gradient">
                {costLoading ? <Skeleton className="h-8 w-24" /> : costSummary ? formatCurrency(costSummary.total_monthly_cost) : "---"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">From latest analysis</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass h-full relative overflow-hidden group hover:border-success/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
              <TrendingDown className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {costLoading ? <Skeleton className="h-8 w-24" /> : costSummary ? formatCurrency(costSummary.potential_savings) : "---"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Estimated monthly reduction</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass h-full relative overflow-hidden group hover:border-warning/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Findings</CardTitle>
              <ShieldAlert className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {findingsLoading ? <Skeleton className="h-8 w-12" /> : findings?.length || "---"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Optimization targets</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass h-full relative overflow-hidden group hover:border-info/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">FinOps Score</CardTitle>
              <Gauge className="h-4 w-4 text-info" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {scoreLoading ? <Skeleton className="h-8 w-12" /> : score ? `${score.overall_score}/100` : "---"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Overall health</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-3 lg:grid-cols-7">
        {/* Charts Section */}
        <motion.div variants={itemVariants} className="md:col-span-2 lg:col-span-4 space-y-6">
          <Card className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><BarChart4 className="w-5 h-5" /> Top Savings Opportunities</CardTitle>
              <CardDescription>Highest value findings from the most recent analysis scan.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full">
                {findingsLoading ? (
                  <div className="w-full h-full flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
                ) : topSavings.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={topSavings} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--color-border)" />
                      <XAxis type="number" tickFormatter={(val) => `$${val}`} stroke="var(--color-muted-foreground)" fontSize={12} />
                      <YAxis dataKey="title" type="category" width={150} stroke="var(--color-muted-foreground)" fontSize={11} tickFormatter={(v) => v.length > 20 ? v.substring(0,20)+'...' : v} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "8px" }}
                        formatter={(value: unknown) => [formatCurrency(Number(value) || 0), "Savings"]}
                        cursor={{ fill: 'var(--color-muted)' }}
                      />
                      <Bar dataKey="estimated_monthly_savings" fill="var(--color-success)" radius={[0, 4, 4, 0]} barSize={24} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground">
                    <Activity className="w-12 h-12 mb-4 opacity-20" />
                    <p>No savings data available</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Action & Findings Breakdown */}
        <motion.div variants={itemVariants} className="md:col-span-1 lg:col-span-3 space-y-6">
          <Card className="glass relative overflow-hidden border-primary/20">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-chart-2" />
            <CardHeader>
              <CardTitle>Run Analysis</CardTitle>
              <CardDescription>Scan infrastructure for cost anomalies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Subscription</Label>
                <Select disabled={subsLoading} value={selectedSub} onValueChange={(val) => { setSelectedSub(val || ""); setSelectedRg(""); }}>
                  <SelectTrigger className="bg-background">
                    <SelectValue placeholder="Select a subscription" />
                  </SelectTrigger>
                  <SelectContent>
                    {subscriptions?.map((sub) => (
                      <SelectItem key={sub.subscription_id} value={sub.subscription_id}>{sub.display_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Resource Group</Label>
                <Select disabled={!selectedSub || rgsLoading} value={selectedRg} onValueChange={(val) => setSelectedRg(val || "")}>
                  <SelectTrigger className="bg-background">
                    <SelectValue placeholder="All Resource Groups" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Resource Groups</SelectItem>
                    {resourceGroups?.map((rg) => (
                      <SelectItem key={rg.name} value={rg.name}>{rg.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button 
                aria-label="Run new FinOps analysis scan"
                className="w-full mt-4 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-lg shadow-primary/20" 
                onClick={() => createAnalysis.mutate()}
                disabled={!selectedSub || createAnalysis.isPending}
              >
                {createAnalysis.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4 fill-current" />}
                {createAnalysis.isPending ? "Starting Engine..." : "Analyze Infrastructure"}
              </Button>
            </CardContent>
          </Card>

          <Card className="glass">
            <CardHeader>
              <CardTitle>Findings by Severity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] w-full">
                {findingsLoading ? (
                  <div className="w-full h-full flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-muted-foreground" /></div>
                ) : pieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={severityColors[entry.name] || "var(--color-muted)"} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "8px" }}
                        itemStyle={{ color: "var(--color-foreground)" }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                    No findings recorded
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Analyses Table */}
      <motion.div variants={itemVariants}>
        <Card className="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Clock className="w-5 h-5" /> Recent Scans</CardTitle>
            <CardDescription>History of your latest FinOps analyses.</CardDescription>
          </CardHeader>
          <CardContent>
            {analysesLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : analyses && analyses.length > 0 ? (
              <div className="relative w-full overflow-auto">
                <table className="w-full caption-bottom text-sm">
                  <thead className="[&_tr]:border-b border-border">
                    <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Date</th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Subscription</th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Resource Group</th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                      <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Action</th>
                    </tr>
                  </thead>
                  <tbody className="[&_tr:last-child]:border-0">
                    {analyses.slice(0, 5).map((analysis) => (
                      <tr key={analysis.id} className="border-b border-border/50 transition-colors hover:bg-muted/50">
                        <td className="p-4 align-middle">{new Date(analysis.created_at).toLocaleDateString()}</td>
                        <td className="p-4 align-middle font-mono text-xs">{analysis.subscription_id.split("-")[0]}...</td>
                        <td className="p-4 align-middle">{analysis.resource_group === "all" ? "All Groups" : analysis.resource_group}</td>
                        <td className="p-4 align-middle">
                          <Badge 
                            variant={analysis.status === "completed" ? "default" : analysis.status === "failed" ? "destructive" : "secondary"}
                            className={analysis.status === "completed" ? "bg-success hover:bg-success/80 text-success-foreground" : ""}
                          >
                            {analysis.status}
                          </Badge>
                        </td>
                        <td className="p-4 align-middle text-right">
                          <Button variant="ghost" size="sm" onClick={() => router.push(`/analyses/${analysis.id}`)}>
                            View Report
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                No analyses found. Run your first scan to see insights.
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
