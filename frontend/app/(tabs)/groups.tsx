import { useEffect, useMemo, useState } from "react";
import {
  View,
  StyleSheet,
  FlatList,
  Image,
  TextInput,
  ScrollView,
  TouchableOpacity,
  useWindowDimensions,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import { useThemeColor } from "@/hooks/use-theme-color";

type GroupMode = "two" | "three";

type GroupMember = {
  id: string;
  names: string[];
  images: string[];
  status: string;
  messages: GroupMessage[];
};

type GroupMessage = {
  id: string;
  sender: string;
  text: string;
  isSelf: boolean;
};

type GroupConfig = {
  title: string;
  members: GroupMember[];
};

const groupConfigurations: Record<GroupMode, GroupConfig> = {
  two: {
    title: "2 man's",
    members: [
      {
        id: "andrew",
        names: ["Andrew"],
        images: ["https://randomuser.me/api/portraits/men/22.jpg"],
        status: "Planning tonight's move",
        messages: [
          {
            id: "1",
            sender: "Andrew",
            text: "Slide thru at 9? I got us a section on the patio.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Bet. I'll scoop drinks on the way.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "Andrew",
            text: "Copy. Dress code is chill but keep it sharp.",
            isSelf: false,
          },
        ],
      },
      {
        id: "liam",
        names: ["Liam"],
        images: ["https://randomuser.me/api/portraits/men/32.jpg"],
        status: "En route to the meetup",
        messages: [
          {
            id: "1",
            sender: "Liam",
            text: "Traffic is light. I’ll be there in 10.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Perfect. Grab wristbands at the desk.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "Liam",
            text: "On it. Save me a spot by the DJ.",
            isSelf: false,
          },
        ],
      },
      {
        id: "david",
        names: ["David"],
        images: ["https://randomuser.me/api/portraits/men/41.jpg"],
        status: "Checking the scene",
        messages: [
          {
            id: "1",
            sender: "David",
            text: "Line's moving fast. Vibe is looking good.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Say less. Let me know once you’re inside.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "David",
            text: "Will do. Might grab a booth on the left.",
            isSelf: false,
          },
        ],
      },
      {
        id: "marcus",
        names: ["Marcus"],
        images: ["https://randomuser.me/api/portraits/men/61.jpg"],
        status: "Active now",
        messages: [
          {
            id: "1",
            sender: "Marcus",
            text: "Already inside. Meet me by the bar.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Bet. Need anything while I’m on the way?",
            isSelf: true,
          },
          {
            id: "3",
            sender: "Marcus",
            text: "We’re good. Just bring the energy.",
            isSelf: false,
          },
        ],
      },
    ],
  },
  three: {
    title: "3 man's",
    members: [
      {
        id: "andrew_liam",
        names: ["Andrew", "Liam"],
        images: [
          "https://randomuser.me/api/portraits/men/22.jpg",
          "https://randomuser.me/api/portraits/men/32.jpg",
        ],
        status: "Linked up and ready",
        messages: [
          {
            id: "1",
            sender: "Andrew",
            text: "We running a three-man tonight, right?",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Yeah, meet at the rooftop bar for 8.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "Liam",
            text: "I'll grab the table while you park.",
            isSelf: false,
          },
        ],
      },
      {
        id: "jamal_daniel",
        names: ["Jamal", "Daniel"],
        images: [
          "https://randomuser.me/api/portraits/men/75.jpg",
          "https://randomuser.me/api/portraits/men/28.jpg",
        ],
        status: "Scouting the next spot",
        messages: [
          {
            id: "1",
            sender: "Jamal",
            text: "Daniel and I are peeping the lounge upstairs.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Let me know if it’s worth it or we pivot.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "Daniel",
            text: "Vibes are high—come through.",
            isSelf: false,
          },
        ],
      },
      {
        id: "marcus_david",
        names: ["Marcus", "David"],
        images: [
          "https://randomuser.me/api/portraits/men/61.jpg",
          "https://randomuser.me/api/portraits/men/41.jpg",
        ],
        status: "On standby",
        messages: [
          {
            id: "1",
            sender: "Marcus",
            text: "We’re warming up on the side court.",
            isSelf: false,
          },
          {
            id: "2",
            sender: "You",
            text: "Stay loose. I’ll join after I wrap here.",
            isSelf: true,
          },
          {
            id: "3",
            sender: "David",
            text: "Cool. Text when you’re heading over.",
            isSelf: false,
          },
        ],
      },
    ],
  },
};

export default function GroupsScreen() {
  const [draftMessage, setDraftMessage] = useState("");
  const [groupMode, setGroupMode] = useState<GroupMode>("two");
  const [selectedCrewId, setSelectedCrewId] = useState<string | null>(
    groupConfigurations.two.members[0]?.id ?? null
  );
  const insets = useSafeAreaInsets();
  const { width } = useWindowDimensions();

  const backgroundColor = useThemeColor({}, "background");
  const borderColor = useThemeColor({}, "border");
  const textColor = useThemeColor({}, "text");
  const tintColor = useThemeColor({}, "tint");
  const placeholderColor = useThemeColor(
    { light: "#9A9A9A", dark: "#7A7A7A" },
    "text"
  );
  const sectionBackground = useThemeColor(
    { light: "#F8F8F8", dark: "#1C1C1E" },
    "background"
  );
  const inputBackground = useThemeColor(
    { light: "#FFFFFF", dark: "#1F1F1F" },
    "background"
  );

  const isWideLayout = width >= 768;
  const activeConfig = useMemo(() => groupConfigurations[groupMode], [groupMode]);
  const activeCrew = useMemo(() => {
    return activeConfig.members.find((member) => member.id === selectedCrewId);
  }, [activeConfig, selectedCrewId]);

  useEffect(() => {
    const defaultCrewId = groupConfigurations[groupMode].members[0]?.id ?? null;
    setSelectedCrewId(defaultCrewId);
    setDraftMessage("");
  }, [groupMode]);
  const formatMemberNames = useMemo(
    () => (names: string[]) => {
      if (names.length === 0) return "";
      if (names.length === 1) return names[0];
      if (names.length === 2) return `${names[0]} & ${names[1]}`;
      const head = names.slice(0, -1).join(", ");
      return `${head} & ${names[names.length - 1]}`;
    },
    []
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
        <View style={styles.toggleRow}>
          <View style={styles.toggle}>
            {(["two", "three"] as const).map((mode) => {
              const isActive = groupMode === mode;
              return (
                <TouchableOpacity
                  key={mode}
                  onPress={() => setGroupMode(mode)}
                  style={[
                    styles.toggleButton,
                    {
                      backgroundColor: isActive ? tintColor : sectionBackground,
                      borderColor,
                    },
                  ]}
                  activeOpacity={0.9}
                >
                  <ThemedText
                    type="defaultSemiBold"
                    style={[
                      styles.toggleLabel,
                      isActive && styles.toggleLabelActive,
                    ]}
                  >
                    {groupConfigurations[mode].title}
                  </ThemedText>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        <View style={styles.header}>
          <ThemedText type="title" style={styles.title}>
            {activeConfig.title}
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            Chat with your crew here and let each other know the moves you're
            making.
          </ThemedText>
        </View>

        <View
          style={[
            styles.content,
            isWideLayout ? styles.contentRow : styles.contentStack,
          ]}
        >
          <View
            style={[
              styles.section,
              styles.membersSection,
              { borderColor, backgroundColor: sectionBackground },
            ]}
          >
            <ThemedText type="heading" style={styles.sectionTitle}>
              Crew List
            </ThemedText>
            <FlatList
              data={activeConfig.members}
              keyExtractor={(item) => item.id}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.memberList}
              renderItem={({ item }) => (
                <TouchableOpacity
                  onPress={() => setSelectedCrewId(item.id)}
                  style={[
                    styles.memberRow,
                    selectedCrewId === item.id && styles.memberRowActive,
                  ]}
                  activeOpacity={0.9}
                >
                  <View style={styles.memberAvatarGroup}>
                    {item.images.map((imageUri, index) => (
                      <Image
                        key={`${item.id}-${index}`}
                        source={{ uri: imageUri }}
                        style={[
                          styles.memberAvatar,
                          item.images.length > 1 && styles.memberAvatarSmall,
                          item.images.length > 1 &&
                            index > 0 &&
                            styles.memberAvatarOverlap,
                          selectedCrewId === item.id &&
                            styles.memberAvatarActiveBorder,
                          selectedCrewId === item.id && {
                            borderColor: tintColor,
                          },
                        ]}
                      />
                    ))}
                  </View>
                  <View style={styles.memberMeta}>
                    <ThemedText
                      type="defaultSemiBold"
                      style={styles.memberName}
                      numberOfLines={1}
                    >
                      {formatMemberNames(item.names)}
                    </ThemedText>
                    <ThemedText style={styles.memberStatus}>
                      {item.status}
                    </ThemedText>
                  </View>
                </TouchableOpacity>
              )}
            />
          </View>

          <View
            style={[
              styles.section,
              styles.chatSection,
              { borderColor, backgroundColor: sectionBackground },
            ]}
          >
            <ThemedText type="heading" style={styles.sectionTitle}>
              Messages
            </ThemedText>
            <ScrollView
              style={styles.chatScrollView}
              contentContainerStyle={styles.chatContent}
              showsVerticalScrollIndicator={false}
            >
              {activeCrew?.messages.map((message) => (
                <View
                  key={message.id}
                  style={[
                    styles.messageRow,
                    message.isSelf ? styles.messageRowSelf : styles.messageRowOther,
                  ]}
                >
                  <View
                    style={[
                      styles.messageBubble,
                      {
                        backgroundColor: message.isSelf
                          ? tintColor
                          : sectionBackground,
                        borderColor,
                      },
                    ]}
                  >
                    <ThemedText
                      type="defaultSemiBold"
                      style={[
                        styles.messageSender,
                        message.isSelf && styles.messageSenderOnTint,
                      ]}
                    >
                      {message.sender}
                    </ThemedText>
                    <ThemedText
                      style={[
                        styles.messageText,
                        message.isSelf && styles.messageTextOnTint,
                      ]}
                    >
                      {message.text}
                    </ThemedText>
                  </View>
                </View>
              ))}
              {!activeCrew && (
                <View style={styles.emptyState}>
                  <ThemedText style={styles.emptyStateText}>
                    Pick a crew from the list to start chatting.
                  </ThemedText>
                </View>
              )}
            </ScrollView>

            <View style={[styles.chatInputContainer, { borderColor }] }>
              <TextInput
                value={draftMessage}
                onChangeText={setDraftMessage}
                placeholder="Write a message..."
                placeholderTextColor={placeholderColor}
                style={[
                  styles.chatInput,
                  {
                    backgroundColor: inputBackground,
                    color: textColor,
                    borderColor,
                  },
                ]}
              />
              <TouchableOpacity
                style={[styles.sendButton, { backgroundColor: tintColor }]}
                activeOpacity={0.8}
              >
                <ThemedText style={styles.sendButtonText}>Send</ThemedText>
              </TouchableOpacity>
            </View>
          </View>
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
  header: {
    gap: 8,
    marginBottom: 24,
  },
  toggleRow: {
    marginBottom: 16,
  },
  toggle: {
    flexDirection: "row",
    gap: 8,
  },
  toggleButton: {
    borderRadius: 12,
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
  title: {
    letterSpacing: -0.5,
  },
  subtitle: {
    opacity: 0.7,
  },
  content: {
    flex: 1,
    gap: 16,
  },
  contentStack: {
    flexDirection: "column",
  },
  contentRow: {
    flexDirection: "row",
  },
  section: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 16,
    padding: 20,
  },
  membersSection: {
    maxWidth: 360,
  },
  chatSection: {
    flex: 2,
  },
  sectionTitle: {
    marginBottom: 16,
  },
  memberList: {
    gap: 16,
  },
  memberRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
    marginBottom: 16,
    borderRadius: 12,
    padding: 12,
  },
  memberRowActive: {
    backgroundColor: "rgba(255, 107, 107, 0.08)",
  },
  memberAvatarGroup: {
    flexDirection: "row",
    alignItems: "center",
  },
  memberAvatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
  },
  memberAvatarSmall: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
  memberAvatarOverlap: {
    marginLeft: -18,
  },
  memberAvatarActiveBorder: {
    borderWidth: 2,
  },
  memberMeta: {
    flex: 1,
  },
  memberName: {
    fontSize: 18,
  },
  memberStatus: {
    opacity: 0.6,
  },
  chatScrollView: {
    flex: 1,
  },
  chatContent: {
    gap: 12,
    paddingBottom: 16,
  },
  messageRow: {
    flexDirection: "row",
  },
  messageRowSelf: {
    justifyContent: "flex-end",
  },
  messageRowOther: {
    justifyContent: "flex-start",
  },
  messageBubble: {
    maxWidth: "80%",
    borderRadius: 16,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
  },
  messageSender: {
    marginBottom: 4,
    fontSize: 14,
    opacity: 0.7,
  },
  messageSenderOnTint: {
    color: "#FFFFFF",
    opacity: 0.8,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  messageTextOnTint: {
    color: "#FFFFFF",
  },
  emptyState: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 48,
  },
  emptyStateText: {
    opacity: 0.6,
    textAlign: "center",
  },
  chatInputContainer: {
    marginTop: 16,
    borderTopWidth: 1,
    paddingTop: 16,
    gap: 12,
  },
  chatInput: {
    minHeight: 48,
    borderRadius: 12,
    borderWidth: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
  },
  sendButton: {
    alignSelf: "flex-end",
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontWeight: "600",
  },
});
