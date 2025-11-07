import { useState, useEffect } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { Button } from "@/components/button";
import { Input } from "@/components/input";
import { useAuth } from "@/context/auth-context";

export default function ProfileScreen() {
  const router = useRouter();
  const { user, updateProfile } = useAuth();
  const [age, setAge] = useState("");
  const [bio, setBio] = useState("");
  const [errors, setErrors] = useState<{ age?: string; bio?: string }>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      if (user.age) setAge(user.age.toString());
      if (user.bio) setBio(user.bio);
    }
  }, [user]);

  const validate = () => {
    const newErrors: { age?: string; bio?: string } = {};

    if (!age.trim()) {
      newErrors.age = "Age is required";
    } else {
      const ageNum = parseInt(age, 10);
      if (isNaN(ageNum) || ageNum < 18 || ageNum > 100) {
        newErrors.age = "Please enter a valid age (18-100)";
      }
    }

    if (!bio.trim()) {
      newErrors.bio = "Bio is required";
    } else if (bio.length < 10) {
      newErrors.bio = "Bio must be at least 10 characters";
    } else if (bio.length > 500) {
      newErrors.bio = "Bio must be less than 500 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleComplete = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      await updateProfile({
        age: parseInt(age, 10),
        bio: bio.trim(),
      });
      router.replace("/home" as any);
    } catch (error) {
      console.error("Profile update error:", error);
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.container}>
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
                Complete Your Profile
              </ThemedText>
              <ThemedText style={styles.subtitle}>
                Tell us a bit about yourself to help others get to know you
              </ThemedText>

              <View style={styles.form}>
                <Input
                  label="Age"
                  placeholder="Enter your age"
                  value={age}
                  onChangeText={(text) => {
                    setAge(text.replace(/[^0-9]/g, ""));
                    if (errors.age) setErrors({ ...errors, age: undefined });
                  }}
                  error={errors.age}
                  keyboardType="number-pad"
                  maxLength={3}
                />

                <Input
                  label="Bio"
                  placeholder="Tell us about yourself..."
                  value={bio}
                  onChangeText={(text) => {
                    setBio(text);
                    if (errors.bio) setErrors({ ...errors, bio: undefined });
                  }}
                  error={errors.bio}
                  multiline
                  numberOfLines={6}
                  textAlignVertical="top"
                  style={styles.bioInput}
                  maxLength={500}
                />

                <ThemedText style={styles.charCount}>
                  {bio.length}/500 characters
                </ThemedText>

                <Button
                  title="Complete Profile"
                  onPress={handleComplete}
                  loading={loading}
                  style={styles.button}
                />
              </View>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </ThemedView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
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
  bioInput: {
    minHeight: 120,
    paddingTop: 14,
  },
  charCount: {
    fontSize: 12,
    opacity: 0.5,
    textAlign: "right",
    marginTop: -12,
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
});
