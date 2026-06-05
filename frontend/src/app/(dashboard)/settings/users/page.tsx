"use client"

import { Shield, ShieldAlert, UserCog, UserCheck } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useCurrentUser, useUsers, useUpdateUserRole } from "@/lib/queries"
import { toast } from "sonner"

export default function UserManagementPage() {
  const { data: currentUser } = useCurrentUser()
  const { data: users, isLoading } = useUsers()
  const updateRole = useUpdateUserRole()

  const isAdmin = currentUser?.role === "admin"

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await updateRole.mutateAsync({ userId, role: newRole })
      toast.success("Role updated successfully")
    } catch (error) {
      toast.error("Failed to update user role")
    }
  }

  if (!isAdmin && currentUser) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <ShieldAlert className="w-16 h-16 text-destructive mb-4 opacity-80" />
        <h2 className="text-2xl font-bold">Access Denied</h2>
        <p className="text-muted-foreground mt-2 max-w-md">
          You do not have permission to view or manage tenant users. This area requires Administrator privileges.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight">User Management</h2>
        <p className="text-muted-foreground">Manage roles and permissions for users in your organization.</p>
      </div>

      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><UserCog className="w-5 h-5 text-primary" /> Active Users</CardTitle>
          <CardDescription>
            Users are automatically provisioned via Azure Entra ID upon first login.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          ) : (
            <div className="rounded-md border border-border">
              <table className="w-full text-sm text-left">
                <thead className="bg-muted/50 border-b border-border">
                  <tr>
                    <th className="p-4 font-medium text-muted-foreground">User</th>
                    <th className="p-4 font-medium text-muted-foreground">Email</th>
                    <th className="p-4 font-medium text-muted-foreground w-48">Role</th>
                    <th className="p-4 font-medium text-muted-foreground w-32 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {users?.map((user) => (
                    <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                      <td className="p-4 font-medium">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                            {user.display_name.charAt(0)}
                          </div>
                          {user.display_name}
                          {user.id === currentUser?.id && (
                            <Badge variant="outline" className="ml-2 text-[10px] uppercase py-0 px-1 border-primary/30 text-primary">You</Badge>
                          )}
                        </div>
                      </td>
                      <td className="p-4 text-muted-foreground">{user.email}</td>
                      <td className="p-4">
                        <Select 
                          disabled={user.id === currentUser?.id || updateRole.isPending}
                          value={user.role}
                          onValueChange={(val) => val && handleRoleChange(user.id, val)}
                        >
                          <SelectTrigger className="w-full h-8 bg-background">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">Administrator</SelectItem>
                            <SelectItem value="analyst">Analyst</SelectItem>
                            <SelectItem value="viewer">Viewer</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                      <td className="p-4 text-right">
                        <div className="flex items-center justify-end gap-1.5 text-success">
                          <UserCheck className="w-4 h-4" /> Active
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-muted/10 border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Administrator</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Full access to all FinOps tools, user management, and tenant settings.
          </CardContent>
        </Card>
        <Card className="bg-muted/10 border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Analyst</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Can trigger new analyses, view findings, and export reports.
          </CardContent>
        </Card>
        <Card className="bg-muted/10 border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Viewer</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Read-only access to existing analyses, dashboards, and FinOps scores.
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
