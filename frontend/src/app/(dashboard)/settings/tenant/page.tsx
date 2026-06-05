"use client"

import { Building2, Users, Database, Activity } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useTenantStats } from "@/lib/queries"

export default function TenantSettingsPage() {
  const { data: stats, isLoading } = useTenantStats()

  return (
    <div className="space-y-6 max-w-4xl pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight">Tenant Settings</h2>
        <p className="text-muted-foreground">Manage your organization's workspace and view global usage metrics.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="glass md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Building2 className="w-5 h-5 text-primary" /> Tenant Information</CardTitle>
            <CardDescription>Your unique organization identifier for multi-tenant isolation.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2 max-w-md">
              <Label htmlFor="tenant_id">Tenant ID</Label>
              <Input 
                id="tenant_id" 
                value={isLoading ? "Loading..." : stats?.tenant_id || ""} 
                disabled 
                className="font-mono text-muted-foreground bg-muted/30" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                This ID maps directly to your Azure Entra ID Tenant and scopes all data access.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-10 w-24" /> : (
              <div className="flex items-center gap-4">
                <Users className="w-8 h-8 text-muted-foreground/30" />
                <div className="text-3xl font-bold">{stats?.user_count || 0}</div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Scans Run</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-10 w-24" /> : (
              <div className="flex items-center gap-4">
                <Activity className="w-8 h-8 text-muted-foreground/30" />
                <div className="text-3xl font-bold">{stats?.analysis_count || 0}</div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Database className="w-5 h-5 text-primary" /> Data Retention</CardTitle>
            <CardDescription>Configure how long historical FinOps data is stored.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 border border-border rounded-lg bg-muted/10">
              <div className="space-y-0.5">
                <div className="font-medium">Analysis History</div>
                <div className="text-sm text-muted-foreground">Cost data and findings are retained indefinitely by default.</div>
              </div>
              <div className="text-sm font-medium px-3 py-1 bg-primary/10 text-primary rounded-full">
                Unlimited
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
