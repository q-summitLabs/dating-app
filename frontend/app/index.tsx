import { View, StyleSheet, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { Button } from "@/components/button";
import { useAuth } from "@/context/auth-context";
import { useEffect } from "react";

export default function WelcomeScreen() {
  const router = useRouter();
  const { isAuthenticated, user, loading } = useAuth();

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
      <SafeAreaView style={styles.container}>
        <ThemedView style={styles.container}>
          <ThemedText>Loading...</ThemedText>
        </ThemedView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.container}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.content}>
            {/* Logo placeholder - you can replace this with an actual logo */}
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: "center",
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  logoContainer: {
    flexDirection: "row",
    gap: 16,
    marginBottom: 32,
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
    marginBottom: 16,
    textAlign: "center",
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
