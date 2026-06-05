"use client"

import { useSession, signOut } from "next-auth/react"
import { usePathname } from "next/navigation"
import { Bell, ActivitySquare, ChevronRight, LogOut, Settings, UserCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export function Header() {
  const { data: session } = useSession()
  const pathname = usePathname()
  
  const userInitials = session?.user?.name
    ? session.user.name.split(" ").map((n) => n[0]).join("").toUpperCase().substring(0, 2)
    : "U"

  // Generate Breadcrumbs
  const paths = pathname.split('/').filter(Boolean)
  const breadcrumbs = paths.map(path => {
    return path.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  })
  
  if (breadcrumbs.length === 0) breadcrumbs.push("Dashboard")

  return (
    <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-border/50 bg-background/80 px-6 backdrop-blur-xl">
      <div className="flex flex-1 items-center gap-2 text-sm text-muted-foreground">
        <div className="flex items-center gap-2 bg-muted/30 px-3 py-1.5 rounded-md border border-border/50">
          <ActivitySquare className="h-4 w-4 text-success" />
          <span className="font-medium text-foreground">AI Cost Detective</span>
          {breadcrumbs.map((crumb, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <ChevronRight className="h-3 w-3 text-muted-foreground/50" />
              <span className={idx === breadcrumbs.length - 1 ? "text-foreground font-medium" : ""}>
                {crumb}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="text-muted-foreground relative hover:bg-muted/50 hover:text-foreground transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary ring-2 ring-background animate-pulse"></span>
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger className="relative h-9 w-9 rounded-full ring-2 ring-transparent hover:ring-primary/50 transition-all focus:outline-none">
            <Avatar className="h-9 w-9">
              <AvatarImage src={session?.user?.image || ""} alt={session?.user?.name || ""} />
              <AvatarFallback className="bg-primary/20 text-primary font-bold">{userInitials}</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-64 glass" align="end">
            <DropdownMenuLabel className="font-normal p-3">
              <div className="flex flex-col space-y-1.5">
                <p className="text-sm font-semibold leading-none">{session?.user?.name}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {session?.user?.email}
                </p>
                {session?.tenantId && (
                  <div className="mt-2 inline-flex items-center rounded-md border border-primary/20 bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                    Tenant: {session.tenantId}
                  </div>
                )}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem className="cursor-pointer">
                <UserCircle className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => signOut()} className="cursor-pointer text-destructive focus:bg-destructive/10 focus:text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
