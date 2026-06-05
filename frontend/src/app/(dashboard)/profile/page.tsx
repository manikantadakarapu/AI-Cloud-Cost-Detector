"use client"

import { UserCircle, Mail, Shield, Building2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { useCurrentUser } from "@/lib/queries"
import { Skeleton } from "@/components/ui/skeleton"

export default function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser()

  return (
    <div className="space-y-6 max-w-2xl pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight">Your Profile</h2>
        <p className="text-muted-foreground">Manage your personal account settings and identity context.</p>
      </div>

      <Card className="glass mt-8">
        <CardHeader className="relative pb-10">
          <div className="absolute -top-10 left-6">
            <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-3xl font-bold border-4 border-background shadow-lg">
              {isLoading ? "?" : user?.display_name.charAt(0) || "U"}
            </div>
          </div>
          <div className="pt-8">
            <CardTitle className="text-2xl">{isLoading ? <Skeleton className="h-8 w-48" /> : user?.display_name}</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <Badge variant="outline" className="bg-primary/5 capitalize font-normal border-primary/20 text-primary">
                {isLoading ? "Role" : user?.role}
              </Badge>
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-muted-foreground"><Mail className="w-4 h-4" /> Email Address</Label>
              <Input value={isLoading ? "Loading..." : user?.email} disabled className="bg-muted/30" />
            </div>
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-muted-foreground"><UserCircle className="w-4 h-4" /> Object ID</Label>
              <Input value={isLoading ? "Loading..." : user?.id} disabled className="font-mono text-xs bg-muted/30" />
              <p className="text-xs text-muted-foreground">Unique identifier linked to Azure Entra ID.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border/50 bg-card/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><Shield className="w-4 h-4 text-muted-foreground" /> Authentication & Security</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Your identity is federated through Azure Entra ID (OIDC). Authentication policies, multi-factor authentication (MFA), and password resets are managed entirely within your organization's Microsoft 365 / Azure tenant.
          </p>
          <div className="p-4 bg-muted/30 rounded-md border border-border/50 text-sm">
            Please contact your Azure administrator to modify identity claims or reset credentials.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
