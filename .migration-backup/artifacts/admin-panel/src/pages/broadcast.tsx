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
    if (!confirm("Envoyer ce message à TOUS les utilisateurs approuvés ?")) return

    broadcastMutation.mutate(
      { data: { message } },
      {
        onSuccess: (res) => {
          toast.success("Broadcast envoyé !")
          setResult({ sent: res.sent, failed: res.failed })
          setMessage("")
        },
        onError: () => toast.error("Échec de l'envoi")
      }
    )
  }

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      <Card className="shadow-sm border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-md shrink-0">
              <MessageSquareText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">Broadcast de masse</CardTitle>
              <CardDescription className="text-xs">
                Envoie un message Telegram à tous les utilisateurs approuvés.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder={"Votre message ici...\n\nSupporte le Markdown Telegram :\n**gras**, __italique__, `code`"}
            className="min-h-[200px] font-sans resize-y text-sm"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <div className="flex flex-wrap justify-between items-center gap-2 text-xs text-muted-foreground">
            <span>Markdown : **gras**, __italique__, `code`, [lien](url)</span>
            <span>{message.length} caractères</span>
          </div>

          <Button 
            className="w-full"
            onClick={handleSend} 
            disabled={!message.trim() || broadcastMutation.isPending}
          >
            {broadcastMutation.isPending ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              <Send className="mr-2 h-5 w-5" />
            )}
            {broadcastMutation.isPending ? "Envoi en cours..." : "Envoyer à tous"}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card className="border-emerald-500/20 bg-emerald-500/5 animate-in slide-in-from-bottom-4">
          <CardContent className="p-4">
            <h3 className="font-semibold text-emerald-800 mb-3 text-sm">Résultats</h3>
            <div className="flex flex-wrap gap-2">
              <Badge variant="success" className="text-sm px-3 py-1">
                ✓ {result.sent} envoyés
              </Badge>
              {result.failed > 0 && (
                <Badge variant="destructive" className="text-sm px-3 py-1">
                  ✗ {result.failed} échoués
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
