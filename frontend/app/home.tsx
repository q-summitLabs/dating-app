import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Button } from '@/components/button';
import { useAuth } from '@/context/auth-context';
import { useRouter } from 'expo-router';

export default function HomeScreen() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.replace('/' as any);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.container}>
        <View style={styles.content}>
        <ThemedText type="title" style={styles.title}>
          Welcome, {user?.name}!
        </ThemedText>
        <ThemedText style={styles.subtitle}>
          Your profile is complete. This is where the main app will be.
        </ThemedText>
        <Button
          title="Sign Out"
          variant="outline"
          onPress={handleSignOut}
          style={styles.button}
        />
        </View>
      </ThemedView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    marginBottom: 16,
    textAlign: 'center',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 32,
    opacity: 0.7,
  },
  button: {
    marginTop: 16,
  },
});

