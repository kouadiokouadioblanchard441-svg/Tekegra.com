import { useState } from "react"
import { useAdminLogin } from "@/lib/api-client-react/src/generated/api"
import { useLocation } from "wouter"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

export default function Login() {
  const [, setLocation] = useLocation()
  const [password, setPassword] = useState("")
  const loginMutation = useAdminLogin()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!password.trim()) return

    loginMutation.mutate(
      { data: { password } },
      {
        onSuccess: (res) => {
          localStorage.setItem("admin_token", res.token)
          toast.success("Login successful")
          setLocation("/")
        },
        onError: () => {
          toast.error("Invalid password")
        }
      }
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md shadow-lg border-primary/10">
        <CardHeader className="space-y-2 text-center pb-8">
          <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-2">
            <div className="w-6 h-6 bg-primary rounded-sm shadow-sm" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Admin Login</CardTitle>
          <CardDescription>
            Enter the secure admin password to continue
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loginMutation.isPending || !password.trim()}
            >
              {loginMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
