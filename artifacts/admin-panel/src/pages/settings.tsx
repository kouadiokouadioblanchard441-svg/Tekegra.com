import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { useGetSettings, useUpdateSettings, getGetSettingsQueryKey } from "@/lib/api-client-react/src/generated/api"
import { useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import { Loader2, Save, Image as ImageIcon, Lock } from "lucide-react"
import { Loader } from "@/components/ui/loader"
import { customFetch } from "@workspace/api-client-react"

export default function Settings() {
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useGetSettings()
  const updateMutation = useUpdateSettings()
  const [pwdLoading, setPwdLoading] = useState(false)

  const { register, handleSubmit, reset, formState: { isDirty } } = useForm({
    defaultValues: settings || {}
  })

  const {
    register: registerPwd,
    handleSubmit: handlePwdSubmit,
    reset: resetPwd,
    formState: { errors: pwdErrors },
    watch,
  } = useForm<{ currentPassword: string; newPassword: string; confirmPassword: string }>()

  const newPasswordValue = watch("newPassword")

  const onChangePassword = async (data: { currentPassword: string; newPassword: string; confirmPassword: string }) => {
    if (data.newPassword !== data.confirmPassword) {
      toast.error("Les nouveaux mots de passe ne correspondent pas")
      return
    }
    setPwdLoading(true)
    try {
      await customFetch("/api/admin/change-password", {
        method: "POST",
        body: JSON.stringify({ currentPassword: data.currentPassword, newPassword: data.newPassword }),
        headers: { "Content-Type": "application/json" },
      })
      toast.success("Mot de passe mis à jour avec succès")
      resetPwd()
    } catch (e: any) {
      toast.error(e?.message || "Erreur lors du changement de mot de passe")
    } finally {
      setPwdLoading(false)
    }
  }

  useEffect(() => {
    if (settings) reset(settings)
  }, [settings, reset])

  const onSubmit = (data: any) => {
    const payload = {
      promoCode: data.promoCode,
      affiliateLink: data.affiliateLink,
      freeSignalsPerDay: Number(data.freeSignalsPerDay),
      premiumSignalsPerDay: Number(data.premiumSignalsPerDay),
      channel1Link: data.channel1Link,
      channel1Name: data.channel1Name,
      channel2Link: data.channel2Link,
      channel2Name: data.channel2Name,
      supportUsername: data.supportUsername,
      price7DaysFcfa: Number(data.price7DaysFcfa),
      price30DaysFcfa: Number(data.price30DaysFcfa),
    }
    updateMutation.mutate(
      { data: payload },
      {
        onSuccess: (updatedData) => {
          toast.success("Paramètres enregistrés")
          queryClient.setQueryData(getGetSettingsQueryKey(), updatedData)
          reset(updatedData)
        },
        onError: () => toast.error("Erreur lors de l'enregistrement")
      }
    )
  }

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader className="h-8 w-8" /></div>
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-4">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Header — stacks on mobile */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Configuration</h2>
            <p className="text-sm text-muted-foreground">Liens, limites et comportement du bot.</p>
          </div>
          <Button type="submit" disabled={!isDirty || updateMutation.isPending} className="w-full sm:w-auto">
            {updateMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            Enregistrer
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="shadow-sm border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Monétisation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="promoCode">Code promo 1WIN</Label>
                <Input id="promoCode" {...register("promoCode")} placeholder="ex: VIP2024" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="affiliateLink">Lien d'affiliation</Label>
                <Input id="affiliateLink" {...register("affiliateLink")} placeholder="https://1w..." />
              </div>
              <div className="space-y-2">
                <Label htmlFor="supportUsername">Username Telegram support (paiements)</Label>
                <Input id="supportUsername" {...register("supportUsername")} placeholder="ex: monusername (sans @)" />
                <p className="text-xs text-muted-foreground">Affiché dans le message d'activation Premium pour que les utilisateurs te contactent.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-1 border-t">
                <div className="space-y-2">
                  <Label htmlFor="price7DaysFcfa">Prix abonnement 7 jours (FCFA)</Label>
                  <Input id="price7DaysFcfa" type="number" {...register("price7DaysFcfa")} placeholder="ex: 5594" />
                  <p className="text-xs text-muted-foreground">Affiché tel quel dans le bot</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="price30DaysFcfa">Prix abonnement 30 jours (FCFA)</Label>
                  <Input id="price30DaysFcfa" type="number" {...register("price30DaysFcfa")} placeholder="ex: 16794" />
                  <p className="text-xs text-muted-foreground">Affiché tel quel dans le bot</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Limites de signaux</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="freeSignalsPerDay">Signaux gratuits / jour</Label>
                <Input id="freeSignalsPerDay" type="number" {...register("freeSignalsPerDay")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="premiumSignalsPerDay">Signaux premium / jour</Label>
                <Input id="premiumSignalsPerDay" type="number" {...register("premiumSignalsPerDay")} />
                <p className="text-xs text-muted-foreground">Mettre élevé pour "illimité"</p>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-border/50 lg:col-span-2">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Canaux requis</CardTitle>
              <CardDescription>Canaux auxquels les utilisateurs doivent s'abonner</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3 p-4 border rounded-md bg-muted/20">
                <div className="font-medium text-sm">Canal principal</div>
                <div className="space-y-2">
                  <Label>Nom du canal</Label>
                  <Input {...register("channel1Name")} placeholder="Signaux Officiels" />
                </div>
                <div className="space-y-2">
                  <Label>Lien du canal</Label>
                  <Input {...register("channel1Link")} placeholder="https://t.me/..." />
                </div>
              </div>
              <div className="space-y-3 p-4 border rounded-md bg-muted/20">
                <div className="font-medium text-sm">Canal secondaire</div>
                <div className="space-y-2">
                  <Label>Nom du canal</Label>
                  <Input {...register("channel2Name")} placeholder="Canal VIP" />
                </div>
                <div className="space-y-2">
                  <Label>Lien du canal</Label>
                  <Input {...register("channel2Link")} placeholder="https://t.me/..." />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>

      {/* Change password */}
      <Card className="shadow-sm border-border/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Lock className="h-4 w-4 text-muted-foreground" /> Changer le mot de passe
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePwdSubmit(onChangePassword)} className="space-y-4 max-w-sm">
            <div className="space-y-2">
              <Label>Mot de passe actuel</Label>
              <Input
                type="password"
                {...registerPwd("currentPassword", { required: true })}
                autoComplete="current-password"
              />
            </div>
            <div className="space-y-2">
              <Label>Nouveau mot de passe</Label>
              <Input
                type="password"
                {...registerPwd("newPassword", { required: true, minLength: 6 })}
                autoComplete="new-password"
              />
              {pwdErrors.newPassword?.type === "minLength" && (
                <p className="text-xs text-destructive">Minimum 6 caractères</p>
              )}
            </div>
            <div className="space-y-2">
              <Label>Confirmer le mot de passe</Label>
              <Input
                type="password"
                {...registerPwd("confirmPassword", {
                  required: true,
                  validate: (v) => v === newPasswordValue || "Les mots de passe ne correspondent pas",
                })}
                autoComplete="new-password"
              />
              {pwdErrors.confirmPassword && (
                <p className="text-xs text-destructive">{pwdErrors.confirmPassword.message}</p>
              )}
            </div>
            <Button type="submit" disabled={pwdLoading} className="w-full sm:w-auto">
              {pwdLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lock className="mr-2 h-4 w-4" />}
              Mettre à jour
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Banners (read only) */}
      <Card className="shadow-sm border-border/50 bg-slate-50/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <ImageIcon className="h-4 w-4 text-muted-foreground" /> Bannières actives
          </CardTitle>
          <CardDescription>Pour modifier, envoyez une nouvelle photo directement au bot via Telegram.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {['menuBanner', 'registerBanner', 'luckyjetBanner', 'minesBanner', 'guideBanner'].map((banner) => (
              <div key={banner} className="space-y-1 p-3 border bg-card rounded-md overflow-hidden">
                <div className="text-xs font-medium text-muted-foreground capitalize">
                  {banner.replace('Banner', ' Banner')}
                </div>
                <div
                  className="text-xs font-mono truncate bg-muted p-1.5 rounded"
                  title={(settings as any)?.[banner] || 'Non défini'}
                >
                  {(settings as any)?.[banner] || <span className="text-muted-foreground italic">Non défini</span>}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
