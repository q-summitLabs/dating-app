import { TouchableOpacity, StyleSheet, ActivityIndicator, type TouchableOpacityProps } from 'react-native';
import { ThemedText } from './themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';

type ButtonProps = TouchableOpacityProps & {
  title: string;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
};

export function Button({ title, variant = 'primary', loading, disabled, style, ...props }: ButtonProps) {
  const primaryColor = useThemeColor({}, 'primary');
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const borderColor = useThemeColor({}, 'border');

  const getButtonStyle = () => {
    switch (variant) {
      case 'primary':
        return { backgroundColor: primaryColor };
      case 'secondary':
        return { backgroundColor: 'transparent', borderWidth: 1, borderColor: borderColor };
      case 'outline':
        return { backgroundColor: 'transparent', borderWidth: 2, borderColor: primaryColor };
      default:
        return { backgroundColor: primaryColor };
    }
  };

  const getTextColor = () => {
    switch (variant) {
      case 'primary':
        return '#FFFFFF';
      case 'secondary':
        return textColor;
      case 'outline':
        return primaryColor;
      default:
        return '#FFFFFF';
    }
  };

  return (
    <TouchableOpacity
      style={[styles.button, getButtonStyle(), disabled && styles.disabled, style]}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} />
      ) : (
        <ThemedText style={[styles.buttonText, { color: getTextColor() }]}>
          {title}
        </ThemedText>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  disabled: {
    opacity: 0.5,
  },
});

