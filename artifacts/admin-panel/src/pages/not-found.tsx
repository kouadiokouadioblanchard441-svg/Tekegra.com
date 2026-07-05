import { useLocation } from "wouter"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  const [, setLocation] = useLocation()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground space-y-4">
      <h1 className="text-6xl font-bold text-primary">404</h1>
      <p className="text-xl text-muted-foreground">Page not found</p>
      <Button onClick={() => setLocation("/")} variant="default" className="mt-4">
        Return to Dashboard
      </Button>
    </div>
  )
}
