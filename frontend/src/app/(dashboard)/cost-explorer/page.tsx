"use client"

import { motion } from "framer-motion"
import { DollarSign, BarChart3, Info } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

import { useAnalyses, useAnalysisCostSummary } from "@/lib/queries"

export default function CostExplorerPage() {
  const { data: analyses, isLoading: analysesLoading } = useAnalyses()
  const latestAnalysis = analyses?.find(a => a.status === "completed")
  const latestId = latestAnalysis?.id || ""

  const { data: costSummary, isLoading: costLoading } = useAnalysisCostSummary(latestId, !!latestId)
  const isLoading = analysesLoading || costLoading

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="w-8 h-8 text-primary" /> Cost Explorer
        </h2>
        <p className="text-muted-foreground">Analyze your Azure cloud spend across subscriptions and resource groups.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="glass md:col-span-2">
          <CardHeader>
            <CardTitle>Current Monthly Run Rate</CardTitle>
            <CardDescription>Based on the latest discovery scan.</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center h-48">
            {isLoading ? (
              <Skeleton className="h-16 w-48" />
            ) : !latestId ? (
              <div className="text-center text-muted-foreground flex flex-col items-center">
                <Info className="w-8 h-8 mb-2 opacity-50" />
                <p>No completed analyses available.</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="text-5xl font-bold text-gradient">
                  {costSummary ? formatCurrency(costSummary.total_monthly_cost) : "---"}
                </div>
                <p className="text-muted-foreground mt-2">Amortized monthly cost</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass border-success/20">
          <CardHeader>
            <CardTitle className="text-success flex items-center gap-2">
              <DollarSign className="w-5 h-5" /> Optimization Potential
            </CardTitle>
            <CardDescription>If all findings are remediated.</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center h-48">
            {isLoading ? (
              <Skeleton className="h-16 w-32" />
            ) : !latestId ? (
              <span className="text-muted-foreground">---</span>
            ) : (
              <div className="text-center">
                <div className="text-4xl font-bold text-success">
                  {costSummary ? formatCurrency(costSummary.potential_savings) : "---"}
                </div>
                <p className="text-sm text-success/80 mt-2">per month</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="glass opacity-50 pointer-events-none">
        <CardHeader>
          <CardTitle>Resource Cost Breakdown (Future Enhancement)</CardTitle>
          <CardDescription>Detailed service-level cost analytics require additional backend aggregation endpoints.</CardDescription>
        </CardHeader>
        <CardContent className="h-64 flex items-center justify-center border-t border-dashed border-border bg-muted/10 m-6 mt-0 rounded-b-lg">
          <span className="text-muted-foreground font-medium">Cost timeseries visualization coming soon</span>
        </CardContent>
      </Card>
    </div>
  )
}
