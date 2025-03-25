public class UserProfileContext {
    private static final ThreadLocal<UserProfile> userProfileHolder = new ThreadLocal<>();

    public static void setUserProfile(UserProfile userProfile) {
        userProfileHolder.set(userProfile);
    }

    public static UserProfile getUserProfile() {
        return userProfileHolder.get();
    }

    public static void clear() {
        userProfileHolder.remove();
    }
}