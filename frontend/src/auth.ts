import NextAuth from "next-auth"
import AzureADProvider from "next-auth/providers/azure-ad"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    AzureADProvider({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      issuer: `https://login.microsoftonline.com/${process.env.AZURE_AD_TENANT_ID}/v2.0`,
      authorization: {
        params: {
          scope: `openid profile email ${process.env.AZURE_AD_CLIENT_ID}/.default`,
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token as string | undefined;
        token.tenantId = (account.tenant_id as string | undefined) || process.env.AZURE_AD_TENANT_ID;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.accessToken = token.accessToken as string
        session.tenantId = token.tenantId as string
      }
      return session
    },
  },
})
