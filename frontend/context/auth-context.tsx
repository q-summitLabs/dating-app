import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

type BackendUser = {
  id: number;
  name: string;
  email: string;
  phone_number?: string | null;
  interests?: string[] | null;
  location?: string | null;
  pictures?: string[] | null;
  prompts?: Record<string, unknown> | null;
};

type User = {
  id: number;
  email: string;
  name: string;
  phoneNumber?: string;
  interests?: string[];
  location?: string;
  pictures?: string[];
  prompts?: Record<string, unknown>;
  age?: number;
  bio?: string;
};

type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
};

type AuthResponse = {
  tokens: AuthTokens;
  user: BackendUser;
};

type AuthActionResult = {
  success: boolean;
  message?: string;
};

type AuthContextType = {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  signUp: (
    email: string,
    password: string,
    name: string
  ) => Promise<AuthActionResult>;
  signIn: (email: string, password: string) => Promise<AuthActionResult>;
  updateProfile: (profile: Partial<User>) => Promise<void>;
  signOut: () => Promise<void>;
  loading: boolean;
};

const API_BASE_URL =
  (process.env.EXPO_PUBLIC_API_URL &&
  process.env.EXPO_PUBLIC_API_URL.trim().length > 0
    ? process.env.EXPO_PUBLIC_API_URL.trim()
    : undefined) ?? "http://localhost:8080";
const USER_STORAGE_KEY = "user";
const TOKEN_STORAGE_KEY = "authTokens";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const mapBackendUserToUser = (backendUser: BackendUser): User => ({
  id: backendUser.id,
  email: backendUser.email,
  name: backendUser.name,
  phoneNumber: backendUser.phone_number ?? undefined,
  interests: backendUser.interests ?? undefined,
  location: backendUser.location ?? undefined,
  pictures: backendUser.pictures ?? undefined,
  prompts: backendUser.prompts ?? undefined,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const storedValues = await AsyncStorage.multiGet([
        USER_STORAGE_KEY,
        TOKEN_STORAGE_KEY,
      ]);
      const storedUser = storedValues.find(
        ([key]) => key === USER_STORAGE_KEY
      )?.[1];
      const storedTokens = storedValues.find(
        ([key]) => key === TOKEN_STORAGE_KEY
      )?.[1];

      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
      if (storedTokens) {
        setTokens(JSON.parse(storedTokens));
      }
    } catch (error) {
      console.error("Error loading auth state:", error);
    } finally {
      setLoading(false);
    }
  };

  const persistAuth = async (data: AuthResponse) => {
    const mappedUser = mapBackendUserToUser(data.user);
    await AsyncStorage.multiSet([
      [USER_STORAGE_KEY, JSON.stringify(mappedUser)],
      [TOKEN_STORAGE_KEY, JSON.stringify(data.tokens)],
    ]);
    setUser(mappedUser);
    setTokens(data.tokens);
  };

  const handleErrorResponse = async (
    response: Response,
    defaultMessage: string
  ): Promise<string> => {
    let message: string = defaultMessage;

    try {
      const errorData = await response.json();
      const detail = errorData?.detail;

      if (typeof detail === "string" && detail.trim().length > 0) {
        message = detail.trim();
      } else if (Array.isArray(detail) && detail.length > 0) {
        const firstError = detail[0];
        if (
          typeof firstError?.msg === "string" &&
          firstError.msg.trim().length > 0
        ) {
          message = firstError.msg.trim();
        }
      } else if (
        detail &&
        typeof detail === "object" &&
        Object.keys(detail).length > 0
      ) {
        const firstValue = Object.values(detail).find(
          (value) => typeof value === "string" && value.trim().length > 0
        );
        if (typeof firstValue === "string") {
          message = firstValue.trim();
        }
      }
    } catch {
      // Ignore JSON parse errors and fall back to default message.
    }

    return String(message);
  };

  const buildFailureResult = (
    message: string,
    fallback: string
  ): AuthActionResult => ({
    success: false,
    message: message && message.trim().length > 0 ? message : fallback,
  });

  const signUp = async (
    email: string,
    password: string,
    name: string
  ): Promise<AuthActionResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        const message = await handleErrorResponse(
          response,
          "Unable to sign up. Please try again."
        );
        return buildFailureResult(
          message,
          "Unable to sign up. Please try again."
        );
      }

      const data = (await response.json()) as AuthResponse;
      await persistAuth(data);
      return { success: true };
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : "Unable to sign up. Please try again.";
      return buildFailureResult(
        message,
        "Unable to sign up. Please try again."
      );
    }
  };

  const signIn = async (
    email: string,
    password: string
  ): Promise<AuthActionResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const message = await handleErrorResponse(
          response,
          "Unable to sign in. Please try again."
        );
        return buildFailureResult(
          message,
          "Unable to sign in. Please try again."
        );
      }

      const data = (await response.json()) as AuthResponse;
      await persistAuth(data);
      return { success: true };
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : "Unable to sign in. Please try again.";
      return buildFailureResult(
        message,
        "Unable to sign in. Please try again."
      );
    }
  };

  const updateProfile = async (profile: Partial<User>) => {
    if (!user) return;
    const updatedUser = { ...user, ...profile };
    await AsyncStorage.setItem(USER_STORAGE_KEY, JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  const signOut = async () => {
    await AsyncStorage.multiRemove([USER_STORAGE_KEY, TOKEN_STORAGE_KEY]);
    setUser(null);
    setTokens(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tokens,
        isAuthenticated: !!user,
        signUp,
        signIn,
        updateProfile,
        signOut,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
