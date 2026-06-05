"use client"

import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Clock, Search, ExternalLink } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

import { useAnalyses } from "@/lib/queries"

export default function AnalysisHistoryPage() {
  const router = useRouter()
  const { data: analyses, isLoading } = useAnalyses()

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">Analysis History</h2>
        <p className="text-muted-foreground">View and manage past FinOps scans across your subscriptions.</p>
      </div>

      <Card className="glass border-border/50">
        <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-border/50">
          <div>
            <CardTitle className="text-xl">All Scans</CardTitle>
            <CardDescription>A complete log of all resource discoveries and evaluations.</CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Filter by subscription..."
              className="pl-8 bg-background"
            />
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-md" />
              ))}
            </div>
          ) : analyses && analyses.length > 0 ? (
            <div className="rounded-md border border-border">
              <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b border-border bg-muted/20">
                  <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[150px]">Date Started</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Analysis ID</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Scope</th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[120px]">Status</th>
                    <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground w-[100px]">Action</th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {analyses.map((analysis) => (
                    <motion.tr 
                      key={analysis.id} 
                      className="border-b border-border/50 transition-colors hover:bg-muted/30 group"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <td className="p-4 align-middle whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <Clock className="w-3 h-3 text-muted-foreground" />
                          <span>{new Date(analysis.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="text-xs text-muted-foreground ml-5">{new Date(analysis.created_at).toLocaleTimeString()}</div>
                      </td>
                      <td className="p-4 align-middle font-mono text-xs text-muted-foreground">
                        {analysis.id}
                      </td>
                      <td className="p-4 align-middle">
                        <div className="font-medium text-sm">{analysis.subscription_id}</div>
                        <div className="text-xs text-muted-foreground mt-0.5">
                          RG: {analysis.resource_group === "all" ? "All Groups" : analysis.resource_group}
                        </div>
                      </td>
                      <td className="p-4 align-middle">
                        <Badge 
                          variant={analysis.status === "completed" ? "default" : analysis.status === "failed" ? "destructive" : "secondary"}
                          className={analysis.status === "completed" ? "bg-success hover:bg-success/80 text-success-foreground" : ""}
                        >
                          {analysis.status}
                        </Badge>
                      </td>
                      <td className="p-4 align-middle text-right">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => router.push(`/analyses/${analysis.id}`)}
                        >
                          <ExternalLink className="w-4 h-4 text-primary" />
                        </Button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center border rounded-md border-dashed border-border/50 bg-muted/10 flex flex-col items-center">
              <Search className="w-8 h-8 text-muted-foreground/50 mb-3" />
              <h3 className="text-lg font-medium">No analyses found</h3>
              <p className="text-sm text-muted-foreground max-w-sm mt-1 mb-4">
                You haven't run any resource analyses yet. Head back to the dashboard to start your first FinOps scan.
              </p>
              <Button variant="outline" onClick={() => router.push("/")}>Go to Dashboard</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
