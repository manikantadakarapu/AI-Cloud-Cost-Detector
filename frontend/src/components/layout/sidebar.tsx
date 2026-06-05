"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { LayoutDashboard, FileSearch, PieChart, ShieldAlert, Settings, Users, UserCircle, Gauge } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Analysis History", href: "/analyses", icon: FileSearch },
  { name: "Findings", href: "/findings", icon: ShieldAlert },
  { name: "Cost Explorer", href: "/cost-explorer", icon: PieChart },
  { name: "FinOps Score", href: "/finops-score", icon: Gauge },
]

const settingsNav = [
  { name: "Tenant Settings", href: "/settings/tenant", icon: Settings },
  { name: "User Management", href: "/settings/users", icon: Users },
  { name: "Profile", href: "/profile", icon: UserCircle },
]

function SidebarNavItem({ 
  item, 
  isActive, 
  onClick 
}: { 
  item: { name: string, href: string, icon: any }, 
  isActive: boolean,
  onClick?: () => void
}) {
  return (
    <Link
      href={item.href}
      className="relative group"
      onClick={onClick}
      aria-current={isActive ? "page" : undefined}
    >
      {isActive && (
        <motion.div 
          layoutId="sidebar-active-bg"
          className="absolute inset-0 bg-primary/10 rounded-md border border-primary/20"
          initial={false}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      )}
      <div className={cn(
        "relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors z-10",
        isActive
          ? "text-primary"
          : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
      )}>
        <item.icon className={cn(
          "h-4 w-4 transition-transform duration-200", 
          isActive ? "text-primary" : "text-muted-foreground group-hover:scale-110"
        )} />
        {item.name}
      </div>
    </Link>
  )
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r border-border/50 bg-background/80 backdrop-blur-xl z-20 shadow-2xl md:shadow-none">
      <div className="flex h-14 items-center border-b border-border/50 px-6">
        <Link href="/" className="flex items-center gap-2 font-bold tracking-tight text-primary" onClick={onNavigate}>
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <FileSearch className="h-5 w-5 text-primary" />
          </div>
          <span>Cost Detective</span>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-6 custom-scrollbar">
        <nav className="grid gap-1.5 px-4">
          <p className="px-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 mb-2">Overview</p>
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
            return <SidebarNavItem key={item.name} item={item} isActive={isActive} onClick={onNavigate} />
          })}
        </nav>

        <nav className="grid gap-1.5 px-4 mt-10">
          <p className="px-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 mb-2">Settings</p>
          {settingsNav.map((item) => {
            const isActive = pathname === item.href
            return <SidebarNavItem key={item.name} item={item} isActive={isActive} onClick={onNavigate} />
          })}
        </nav>
      </div>
    </div>
  )
}
