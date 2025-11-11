import { View, StyleSheet } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { Button } from "@/components/button";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "expo-router";
import { useThemeColor } from "@/hooks/use-theme-color";

export default function SettingsScreen() {
  const { signOut } = useAuth();
  const router = useRouter();
  const backgroundColor = useThemeColor({}, "background");
  const insets = useSafeAreaInsets();

  const handleSignOut = async () => {
    await signOut();
    router.replace("/" as any);
  };

  return (
    <View style={[styles.root, { backgroundColor }]}>
      <ThemedView
        style={[
          styles.container,
          { paddingTop: insets.top, paddingBottom: insets.bottom },
        ]}
      >
        <View style={styles.content}>
          <ThemedText type="title" style={styles.title}>
            Settings
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            Manage your account preferences and privacy controls here soon.
          </ThemedText>
          <Button
            title="Sign Out"
            variant="outline"
            onPress={handleSignOut}
            style={styles.button}
          />
        </View>
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
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  title: {
    marginBottom: 16,
    textAlign: "center",
  },
  subtitle: {
    textAlign: "center",
    opacity: 0.7,
    marginBottom: 32,
  },
  button: {
    marginTop: 16,
  },
});
