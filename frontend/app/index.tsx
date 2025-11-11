import { View, StyleSheet, ScrollView } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { Button } from "@/components/button";
import { useAuth } from "@/context/auth-context";
import { useThemeColor } from "@/hooks/use-theme-color";
import { useEffect } from "react";

export default function WelcomeScreen() {
  const router = useRouter();
  const { isAuthenticated, user, loading } = useAuth();
  const backgroundColor = useThemeColor({}, "background");
  const insets = useSafeAreaInsets();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated && user) {
        // Check if profile is complete
        if (user.age && user.bio) {
          router.replace("/home" as any);
        } else {
          router.replace("/profile" as any);
        }
      }
    }
  }, [isAuthenticated, user, loading, router]);

  if (loading) {
    return (
      <View style={[styles.root, { backgroundColor }]}>
        <ThemedView
          style={[
            styles.container,
            { paddingTop: insets.top, paddingBottom: insets.bottom },
          ]}
        >
          <ThemedText>Loading...</ThemedText>
        </ThemedView>
      </View>
    );
  }

  return (
    <View style={[styles.root, { backgroundColor }]}>
      <ThemedView
        style={[
          styles.container,
          {
            paddingTop: insets.top + 32,
            paddingBottom: Math.max(insets.bottom, 32),
          },
        ]}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.content}>
            <View style={styles.logoContainer}>
              <View style={styles.logoCircle}>
                <ThemedText type="title" style={styles.logoText}>
                  🥚
                </ThemedText>
              </View>
              <View style={styles.logoCircle}>
                <ThemedText type="title" style={styles.logoText}>
                  🥚
                </ThemedText>
              </View>
            </View>

            <ThemedText type="title" style={styles.title}>
              Yolk
            </ThemedText>
            <ThemedText style={styles.subtitle}>
              Connect with people who get you. Start your journey today.
            </ThemedText>

            <View style={styles.buttonContainer}>
              <Button
                title="Get Started"
                onPress={() => router.push("/signup" as any)}
                style={styles.button}
              />
            </View>
          </View>
        </ScrollView>
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 24,
    paddingVertical: 56,
  },
  content: {
    width: "100%",
    maxWidth: 420,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 8,
  },
  logoContainer: {
    flexDirection: "row",
    gap: 16,
    marginBottom: 40,
    justifyContent: "center",
    width: "100%",
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "#FFE66D",
    justifyContent: "center",
    alignItems: "center",
  },
  logoText: {
    fontSize: 40,
  },
  title: {
    fontSize: 48,
    fontWeight: "700",
    marginTop: 16,
    marginBottom: 16,
    textAlign: "center",
    lineHeight: 56,
  },
  subtitle: {
    fontSize: 18,
    textAlign: "center",
    marginBottom: 48,
    opacity: 0.7,
    lineHeight: 26,
    paddingHorizontal: 16,
  },
  buttonContainer: {
    width: "100%",
    maxWidth: 400,
  },
  button: {
    width: "100%",
  },
});
