import { signIn } from "@/auth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Search, ShieldCheck } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4 relative overflow-hidden">
      {/* Premium Animated Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background z-0" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-info/10 rounded-full blur-[150px] mix-blend-screen pointer-events-none" />
      
      <div className="z-10 w-full max-w-md">
        <Card className="glass border-primary/20 shadow-2xl shadow-primary/10 backdrop-blur-2xl">
          <CardHeader className="space-y-4 text-center pb-8 pt-10">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 text-primary border border-primary/30 shadow-inner">
              <Search className="h-8 w-8" />
            </div>
            <div className="space-y-1.5">
              <CardTitle className="text-3xl font-bold tracking-tight text-gradient">AI Cost Detective</CardTitle>
              <CardDescription className="text-base font-medium">Enterprise FinOps & Cloud Intelligence</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="px-8 pb-8">
            <form
              action={async () => {
                "use server"
                await signIn("azure-ad", { redirectTo: "/" })
              }}
            >
              <Button 
                className="w-full h-12 text-base font-semibold bg-primary hover:bg-primary/90 shadow-lg shadow-primary/20 transition-all active:scale-[0.98]" 
                type="submit"
              >
                Sign in with Azure Entra ID
              </Button>
            </form>
          </CardContent>
          <CardFooter className="justify-center border-t border-border/50 py-4 bg-muted/10 rounded-b-xl">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <ShieldCheck className="w-4 h-4 text-success" />
              <span>Secured by Microsoft Identity</span>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
