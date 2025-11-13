import { useState } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { Button } from "@/components/button";
import { Input } from "@/components/input";
import { useAuth } from "@/context/auth-context";
import { useThemeColor } from "@/hooks/use-theme-color";

export default function LoginScreen() {
  const router = useRouter();
  const { signIn } = useAuth();
  const backgroundColor = useThemeColor({}, "background");
  const insets = useSafeAreaInsets();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string }>(
    {}
  );
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const newErrors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignIn = async () => {
    if (!validate()) return;

    setLoading(true);
    const result = await signIn(email, password);
    setLoading(false);

    if (!result.success) {
      Alert.alert(
        "Sign In Failed",
        result.message ?? "Something went wrong. Please try again."
      );
      return;
    }

    router.replace("/home" as any);
  };

  return (
    <View style={[styles.root, { backgroundColor }]}>
      <ThemedView
        style={[
          styles.container,
          { paddingTop: insets.top, paddingBottom: insets.bottom },
        ]}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.keyboardView}
        >
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
          >
            <View style={styles.content}>
              <ThemedText type="heading" style={styles.title}>
                Welcome Back
              </ThemedText>
              <ThemedText style={styles.subtitle}>
                Sign in to continue your journey
              </ThemedText>

              <View style={styles.form}>
                <Input
                  label="Email"
                  placeholder="Enter your email"
                  value={email}
                  onChangeText={(text) => {
                    setEmail(text);
                    if (errors.email)
                      setErrors({ ...errors, email: undefined });
                  }}
                  error={errors.email}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />

                <Input
                  label="Password"
                  placeholder="Enter your password"
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    if (errors.password)
                      setErrors({ ...errors, password: undefined });
                  }}
                  error={errors.password}
                  secureTextEntry
                  autoCapitalize="none"
                />

                <Button
                  title="Sign In"
                  onPress={handleSignIn}
                  loading={loading}
                  style={styles.button}
                />
              </View>

              <View style={styles.footer}>
                <ThemedText style={styles.footerText}>
                  New to Yolk?{" "}
                  <ThemedText
                    type="link"
                    onPress={() => router.push("/signup" as any)}
                    style={styles.link}
                  >
                    Create an account
                  </ThemedText>
                </ThemedText>
              </View>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </ThemedView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
    maxWidth: 500,
    width: "100%",
    alignSelf: "center",
  },
  title: {
    marginBottom: 8,
    textAlign: "center",
  },
  subtitle: {
    textAlign: "center",
    marginBottom: 32,
    opacity: 0.7,
  },
  form: {
    width: "100%",
  },
  button: {
    marginTop: 8,
  },
  footer: {
    marginTop: 24,
    alignItems: "center",
  },
  footerText: {
    opacity: 0.7,
  },
  link: {
    fontWeight: "600",
  },
});
