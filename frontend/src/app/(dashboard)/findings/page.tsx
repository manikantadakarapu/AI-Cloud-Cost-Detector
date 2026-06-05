"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { 
  ShieldAlert, 
  Search, 
  Filter, 
  ArrowUpDown,
  Download,
  AlertTriangle,
  Info
} from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

import { useAnalyses, useAnalysisFindings } from "@/lib/queries"

export default function FindingsPage() {
  const { data: analyses, isLoading: analysesLoading } = useAnalyses()
  
  // Get latest completed analysis
  const latestAnalysis = analyses?.find(a => a.status === "completed")
  const latestId = latestAnalysis?.id || ""

  const { data: findings, isLoading: findingsLoading } = useAnalysisFindings(latestId, !!latestId)

  const [searchQuery, setSearchQuery] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  
  const isLoading = analysesLoading || findingsLoading

  const filteredFindings = findings?.filter(f => {
    const matchesSearch = f.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          f.resource_id.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesSeverity = severityFilter === "all" || f.severity.toLowerCase() === severityFilter.toLowerCase()
    return matchesSearch && matchesSeverity
  }).sort((a, b) => b.estimated_monthly_savings - a.estimated_monthly_savings) || []

  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'Critical': return 'border-destructive text-destructive'
      case 'High': return 'border-warning text-warning'
      case 'Medium': return 'border-chart-2 text-chart-2'
      case 'Low': return 'border-success text-success'
      default: return 'border-info text-info'
    }
  }

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-8 h-8 text-primary" /> Active Findings
          </h2>
          <p className="text-muted-foreground">Review and remediate optimization opportunities from your latest scan.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" /> Export CSV
          </Button>
        </div>
      </div>

      <Card className="glass">
        <CardHeader className="pb-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle className="text-xl">Latest Scan Results</CardTitle>
              {latestAnalysis && (
                <Badge variant="secondary" className="font-mono text-xs">
                  {new Date(latestAnalysis.created_at).toLocaleDateString()}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search resources or titles..."
                  className="pl-8 bg-background"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={severityFilter} onValueChange={(val) => setSeverityFilter(val || "all")}>
                <SelectTrigger className="w-[140px] bg-background">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-md" />
              ))}
            </div>
          ) : !latestId ? (
            <div className="py-12 text-center border rounded-md border-dashed border-border/50 bg-muted/10">
              <Info className="w-8 h-8 text-muted-foreground/50 mx-auto mb-3" />
              <h3 className="text-lg font-medium">No completed analyses</h3>
              <p className="text-sm text-muted-foreground mt-1">Run an analysis from the dashboard to see findings.</p>
            </div>
          ) : filteredFindings.length > 0 ? (
            <div className="rounded-md border border-border overflow-hidden">
              <table className="w-full text-sm text-left">
                <thead className="bg-muted/50 border-b border-border">
                  <tr>
                    <th className="p-4 font-medium text-muted-foreground w-28">Severity</th>
                    <th className="p-4 font-medium text-muted-foreground w-32">Category</th>
                    <th className="p-4 font-medium text-muted-foreground">Resource & Recommendation</th>
                    <th className="p-4 font-medium text-muted-foreground text-right w-32">
                      <div className="flex items-center justify-end gap-1 cursor-pointer hover:text-foreground">
                        Savings <ArrowUpDown className="w-3 h-3" />
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50 bg-card/30">
                  {filteredFindings.map((f, i) => (
                    <motion.tr 
                      key={f.id} 
                      className="hover:bg-muted/30 transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <td className="p-4 align-top pt-5">
                        <Badge variant="outline" className={getSeverityColor(f.severity)}>{f.severity}</Badge>
                      </td>
                      <td className="p-4 align-top pt-5 text-muted-foreground">{f.category}</td>
                      <td className="p-4">
                        <div className="font-medium text-base mb-1">{f.title}</div>
                        <div className="text-muted-foreground text-sm mb-2">{f.description}</div>
                        <div className="font-mono text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded inline-block">
                          {f.resource_id.split('/').pop()}
                        </div>
                      </td>
                      <td className="p-4 align-top pt-5 text-right font-mono text-success font-semibold">
                        {formatCurrency(f.estimated_monthly_savings)}
                        <div className="text-xs text-muted-foreground font-sans font-normal mt-1">/ month</div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center border rounded-md border-dashed border-border/50 bg-muted/10">
              <p className="text-muted-foreground">No findings match your current filters.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
