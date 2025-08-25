import { interfaces } from "@reactivated";

const DISCORD_INVITE_URL_PREFIXES = [
  "https://discord.gg/",
  "https://discord.com/invite/",
  "https://discordapp.com/invite/",
] as const;

export function extractInviteCodeFromUrl(inviteUrl: string): string | null {
  const trimmedUrl = inviteUrl.trim();

  for (const prefix of DISCORD_INVITE_URL_PREFIXES) {
    if (trimmedUrl.startsWith(prefix)) {
      const code = trimmedUrl.slice(prefix.length);
      // remove any query parameters or fragments
      return code.split("?")[0].split("#")[0] || null;
    }
  }

  return null;
}

export function isValidDiscordInviteUrl(inviteUrl: string): boolean {
  const code = extractInviteCodeFromUrl(inviteUrl);
  return code !== null && code.length > 0;
}

export async function fetchDiscordInviteInfo(
  inviteCode: string,
): Promise<interfaces.TDiscordInviteData> {
  const inviteInfoUrl = `https://discord.com/api/v10/invites/${inviteCode}`;

  try {
    const response = await fetch(inviteInfoUrl);

    if (!response.ok) {
      throw new Error(`Discord API error: ${response.status} ${response.statusText}`);
    }

    const data: unknown = await response.json();
    return data as interfaces.TDiscordInviteData;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch Discord invite info: ${error.message}`);
    }
    throw new Error("Failed to fetch Discord invite info: Unknown error");
  }
}

export async function validateAndFetchDiscordInvite(inviteUrl: string): Promise<{
  isValid: boolean;
  inviteData?: interfaces.TDiscordInviteData;
  error?: string;
}> {
  try {
    if (!isValidDiscordInviteUrl(inviteUrl)) {
      return {
        isValid: false,
        error:
          "Invalid Discord invite URL format. Please use a URL like: https://discord.gg/abc123",
      };
    }

    const inviteCode = extractInviteCodeFromUrl(inviteUrl);
    if (inviteCode === null || inviteCode.length === 0) {
      return {
        isValid: false,
        error: "Could not extract invite code from URL",
      };
    }

    const inviteData = await fetchDiscordInviteInfo(inviteCode);

    return {
      isValid: true,
      inviteData,
    };
  } catch (error) {
    return {
      isValid: false,
      error: error instanceof Error ? error.message : "Unknown error occurred",
    };
  }
}
