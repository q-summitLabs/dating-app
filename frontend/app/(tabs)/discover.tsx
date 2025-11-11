import { useMemo, useState } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { useThemeColor } from "@/hooks/use-theme-color";

type CrewSize = "two" | "three";

type CrewOption = {
  id: string;
  title: string;
  members: string[];
};

type FemaleGroup = {
  id: string;
  names: string[];
  crewSize: CrewSize;
  bio: string;
  images: string[];
  withCrew: {
    id: string;
    title: string;
    members: string[];
  };
};

const maleCrewOptions: Record<CrewSize, CrewOption[]> = {
  two: [
    { id: "andrew_liam", title: "Andrew & Liam", members: ["Andrew", "Liam"] },
    { id: "jamal_daniel", title: "Jamal & Daniel", members: ["Jamal", "Daniel"] },
    { id: "marcus_david", title: "Marcus & David", members: ["Marcus", "David"] },
  ],
  three: [
    {
      id: "core_trio",
      title: "Andrew, Liam & Marcus",
      members: ["Andrew", "Liam", "Marcus"],
    },
    {
      id: "late_night_trio",
      title: "Jamal, Daniel & David",
      members: ["Jamal", "Daniel", "David"],
    },
    {
      id: "weekend_trio",
      title: "Marcus, Andrew & David",
      members: ["Marcus", "Andrew", "David"],
    },
  ],
};

const femaleGroups: FemaleGroup[] = [
  {
    id: "sasha_nina",
    names: ["Sasha", "Nina"],
    crewSize: "two",
    bio: "Dance-floor queens ready to vibe with a confident duo.",
    images: [
      "https://randomuser.me/api/portraits/women/32.jpg",
      "https://randomuser.me/api/portraits/women/15.jpg",
    ],
    withCrew: maleCrewOptions.two[0],
  },
  {
    id: "bella_zoe",
    names: ["Bella", "Zoe"],
    crewSize: "two",
    bio: "Brunch besties hunting for a duo with solid banter.",
    images: [
      "https://randomuser.me/api/portraits/women/44.jpg",
      "https://randomuser.me/api/portraits/women/65.jpg",
    ],
    withCrew: maleCrewOptions.two[1],
  },
  {
    id: "maya_ari",
    names: ["Maya", "Ari"],
    crewSize: "two",
    bio: "Foodies scouting for a downtown crawl with two stand-up guys.",
    images: [
      "https://randomuser.me/api/portraits/women/82.jpg",
      "https://randomuser.me/api/portraits/women/12.jpg",
    ],
    withCrew: maleCrewOptions.two[2],
  },
  {
    id: "alexa_layla_june",
    names: ["Alexa", "Layla", "June"],
    crewSize: "three",
    bio: "After a patio session with a trio that brings the energy.",
    images: [
      "https://randomuser.me/api/portraits/women/21.jpg",
      "https://randomuser.me/api/portraits/women/31.jpg",
      "https://randomuser.me/api/portraits/women/51.jpg",
    ],
    withCrew: maleCrewOptions.three[0],
  },
  {
    id: "tessa_sky_emme",
    names: ["Tessa", "Sky", "Emme"],
    crewSize: "three",
    bio: "Spontaneous night owls looking for a late-night adventure crew.",
    images: [
      "https://randomuser.me/api/portraits/women/52.jpg",
      "https://randomuser.me/api/portraits/women/7.jpg",
      "https://randomuser.me/api/portraits/women/84.jpg",
    ],
    withCrew: maleCrewOptions.three[1],
  },
  {
    id: "lena_noor_rain",
    names: ["Lena", "Noor", "Rain"],
    crewSize: "three",
    bio: "Sunday hike squad seeking chill vibes and good laughs.",
    images: [
      "https://randomuser.me/api/portraits/women/68.jpg",
      "https://randomuser.me/api/portraits/women/19.jpg",
      "https://randomuser.me/api/portraits/women/88.jpg",
    ],
    withCrew: maleCrewOptions.three[2],
  },
];

export default function DiscoverScreen() {
  const [crewSize, setCrewSize] = useState<CrewSize>("two");
  const [selectedCrewId, setSelectedCrewId] = useState<string>(
    maleCrewOptions.two[0].id
  );
  const [likedGroups, setLikedGroups] = useState<Record<string, boolean>>({});
  const backgroundColor = useThemeColor({}, "background");
  const borderColor = useThemeColor({}, "border");
  const textColor = useThemeColor({}, "text");
  const tintColor = useThemeColor({}, "tint");
  const cardBackground = useThemeColor(
    { light: "#FFFFFF", dark: "#1C1C1E" },
    "background"
  );
  const sectionBackground = useThemeColor(
    { light: "#F8F8F8", dark: "#151515" },
    "background"
  );
  const insets = useSafeAreaInsets();

  const crewOptions = useMemo(() => maleCrewOptions[crewSize], [crewSize]);
  const activeCrew = useMemo(
    () => crewOptions.find((crew) => crew.id === selectedCrewId) ?? crewOptions[0],
    [crewOptions, selectedCrewId]
  );

  const filteredGroups = useMemo(
    () => femaleGroups.filter((group) => group.crewSize === crewSize),
    [crewSize]
  );

  return (
    <View style={[styles.root, { backgroundColor }]}>
      <ThemedView
        style={[
          styles.container,
          {
            paddingTop: insets.top,
            paddingBottom: Math.max(insets.bottom, 16),
            paddingHorizontal: 24,
          },
        ]}
      >
        <View style={styles.header}>
          <ThemedText type="title" style={styles.title}>
            Discover crews
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            Choose your crew size and see which squads are down to link.
          </ThemedText>
        </View>

        <View style={[styles.panel, { backgroundColor: sectionBackground }]}>
          <ThemedText type="heading" style={styles.panelTitle}>
            Select your crew
          </ThemedText>
          <View style={styles.toggleRow}>
            {(["two", "three"] as const).map((size) => {
              const isActive = crewSize === size;
              return (
                <TouchableOpacity
                  key={size}
                  onPress={() => {
                    setCrewSize(size);
                    setSelectedCrewId(maleCrewOptions[size][0].id);
                  }}
                  style={[
                    styles.toggleButton,
                    {
                      backgroundColor: isActive ? tintColor : backgroundColor,
                      borderColor,
                    },
                  ]}
                  activeOpacity={0.9}
                >
                  <ThemedText
                    style={[
                      styles.toggleLabel,
                      isActive && styles.toggleLabelActive,
                    ]}
                    type="defaultSemiBold"
                  >
                    {size === "two" ? "2 man" : "3 man"}
                  </ThemedText>
                </TouchableOpacity>
              );
            })}
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.crewSelector}
          >
            {crewOptions.map((crew) => {
              const isSelected = crew.id === activeCrew.id;
              return (
                <TouchableOpacity
                  key={crew.id}
                  onPress={() => setSelectedCrewId(crew.id)}
                  style={[
                    styles.crewChip,
                    {
                      borderColor: isSelected ? tintColor : borderColor,
                      backgroundColor: isSelected ? tintColor : backgroundColor,
                    },
                  ]}
                  activeOpacity={0.9}
                >
                  <ThemedText
                    style={[
                      styles.crewChipText,
                      {
                        color: isSelected ? "#FFFFFF" : textColor,
                      },
                    ]}
                  >
                    {crew.title}
                  </ThemedText>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        <ScrollView
          style={styles.feed}
          contentContainerStyle={styles.feedContent}
          showsVerticalScrollIndicator={false}
        >
          {filteredGroups.map((group, index) => {
            const crew = crewOptions[index % crewOptions.length] ?? activeCrew;
            const isLiked = likedGroups[group.id] ?? false;
            return (
            <View
              key={group.id}
              style={[
                styles.card,
                { backgroundColor: cardBackground, borderColor },
              ]}
            >
              <View style={styles.cardHeader}>
                <View>
                  <ThemedText type="heading" style={styles.cardTitle}>
                    {group.names.join(" & ")}
                  </ThemedText>
                  <ThemedText style={styles.cardSubtitle}>
                    {group.crewSize === "two" ? "2 woman crew" : "3 woman crew"}
                  </ThemedText>
                </View>
                <View style={styles.cardAvatarGroup}>
                  {group.images.map((imageUri, imageIndex) => (
                    <Image
                      key={`${group.id}-${imageIndex}`}
                      source={{ uri: imageUri }}
                      style={[
                        styles.cardAvatar,
                        group.images.length > 1 && styles.cardAvatarSmall,
                        group.images.length > 1 &&
                          imageIndex > 0 &&
                          styles.cardAvatarOverlap,
                      ]}
                    />
                  ))}
                </View>
              </View>
              <ThemedText style={styles.cardBio}>
                {group.bio}
                {"\n"}
                <ThemedText style={styles.cardCrewCallout}>
                  Linking with {crew.title} ({crew.members.join(" • ")})
                </ThemedText>
              </ThemedText>
              <TouchableOpacity
                onPress={() =>
                  setLikedGroups((prev) => ({
                    ...prev,
                    [group.id]: !isLiked,
                  }))
                }
                style={[
                  styles.likeButton,
                  {
                    backgroundColor: isLiked ? tintColor : backgroundColor,
                    borderColor: tintColor,
                  },
                ]}
                activeOpacity={0.85}
              >
                <ThemedText
                  type="defaultSemiBold"
                  style={[
                    styles.likeButtonText,
                    { color: isLiked ? "#FFFFFF" : tintColor },
                  ]}
                >
                  {isLiked ? "Sent" : "Send Like"}
                </ThemedText>
              </TouchableOpacity>
            </View>
          );
        })}
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
    gap: 24,
  },
  header: {
    gap: 8,
    marginTop: 8,
  },
  title: {
    letterSpacing: -0.5,
  },
  subtitle: {
    opacity: 0.7,
  },
  panel: {
    borderRadius: 20,
    padding: 20,
    gap: 16,
  },
  panelTitle: {
    fontSize: 20,
  },
  toggleRow: {
    flexDirection: "row",
    gap: 12,
  },
  toggleButton: {
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
  },
  toggleLabel: {
    fontSize: 16,
  },
  toggleLabelActive: {
    color: "#FFFFFF",
  },
  crewSelector: {
    gap: 12,
    paddingVertical: 4,
  },
  crewChip: {
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 18,
    paddingVertical: 10,
  },
  crewChipText: {
    fontWeight: "600",
  },
  feed: {
    flex: 1,
  },
  feedContent: {
    gap: 16,
    paddingBottom: 32,
  },
  card: {
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    gap: 16,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  cardTitle: {
    fontSize: 24,
  },
  cardSubtitle: {
    opacity: 0.6,
    marginTop: 4,
  },
  cardAvatarGroup: {
    flexDirection: "row",
    alignItems: "center",
  },
  cardAvatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
  },
  cardAvatarSmall: {
    width: 52,
    height: 52,
    borderRadius: 26,
  },
  cardAvatarOverlap: {
    marginLeft: -18,
  },
  cardBio: {
    lineHeight: 22,
  },
  cardCrewCallout: {
    fontWeight: "600",
  },
  likeButton: {
    borderWidth: 1,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  likeButtonText: {
    fontSize: 16,
  },
});
