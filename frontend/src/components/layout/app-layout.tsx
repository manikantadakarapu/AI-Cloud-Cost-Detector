"use client"

import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Sidebar } from "./sidebar"
import { Header } from "./header"

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/5 via-background to-background pointer-events-none"></div>
      
      <Sidebar />
      
      <div className="flex flex-1 flex-col overflow-hidden relative z-10">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-6 relative">
          <div className="mx-auto max-w-7xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {children}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  )
}
