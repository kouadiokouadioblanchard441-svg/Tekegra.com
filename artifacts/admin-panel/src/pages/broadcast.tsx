import { useState } from "react"
import { useSendBroadcast } from "@/lib/api-client-react/src/generated/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { Loader2, Send, MessageSquareText } from "lucide-react"

export default function Broadcast() {
  const [message, setMessage] = useState("")
  const [result, setResult] = useState<{ sent: number, failed: number } | null>(null)
  
  const broadcastMutation = useSendBroadcast()

  const handleSend = () => {
    if (!message.trim()) return

    if (!confirm("Are you sure you want to send this broadcast to ALL approved users?")) {
      return
    }

    broadcastMutation.mutate(
      { data: { message } },
      {
        onSuccess: (res) => {
          toast.success(`Broadcast complete!`)
          setResult({ sent: res.sentCount, failed: res.failedCount })
          setMessage("")
        },
        onError: () => toast.error("Failed to send broadcast")
      }
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <Card className="shadow-sm border-border/50">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-primary/10 rounded-md">
              <MessageSquareText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">Mass Broadcast</CardTitle>
              <CardDescription>Send a direct Telegram message to all approved bot users.</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Textarea
              placeholder="Type your message here... (Markdown is supported)
Example:
**BIG UPDATE!**
We just added new signals for Mines. Go check them out!"
              className="min-h-[250px] font-sans resize-y"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>Supports basic Telegram Markdown (**, __, `, [text](url))</span>
              <span>{message.length} characters</span>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t">
            <Button 
              size="lg" 
              onClick={handleSend} 
              disabled={!message.trim() || broadcastMutation.isPending}
            >
              {broadcastMutation.isPending ? (
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              ) : (
                <Send className="mr-2 h-5 w-5" />
              )}
              {broadcastMutation.isPending ? "Sending Broadcast..." : "Send to All Users"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Card className="border-emerald-500/20 bg-emerald-500/5 animate-in slide-in-from-bottom-4">
          <CardContent className="p-6">
            <h3 className="font-semibold text-emerald-800 mb-2">Broadcast Results</h3>
            <div className="flex gap-4">
              <Badge variant="success" className="text-sm px-3 py-1">
                {result.sent} Delivered Successfully
              </Badge>
              {result.failed > 0 && (
                <Badge variant="destructive" className="text-sm px-3 py-1">
                  {result.failed} Failed / Blocked
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
