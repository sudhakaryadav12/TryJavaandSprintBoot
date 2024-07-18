import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class PostgresDateTimeUpdater {

    private static final String URL = "jdbc:postgresql://localhost:5432/your_database";
    private static final String USER = "your_username";
    private static final String PASSWORD = "your_password";
    private static final String TABLE_NAME = "your_table";

    public static void main(String[] args) {
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            List<String> dateTimeColumns = getDateTimeColumns(conn, TABLE_NAME);
            for (String column : dateTimeColumns) {
                updateColumnToEasternTime(conn, TABLE_NAME, column);
            }
            System.out.println("DateTime columns updated to Eastern Time Zone.");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private static List<String> getDateTimeColumns(Connection conn, String tableName) throws SQLException {
        List<String> dateTimeColumns = new ArrayList<>();
        String query = "SELECT column_name FROM information_schema.columns WHERE table_name = ? AND data_type = 'timestamp without time zone'";
        try (PreparedStatement pstmt = conn.prepareStatement(query)) {
            pstmt.setString(1, tableName);
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                dateTimeColumns.add(rs.getString("column_name"));
            }
        }
        return dateTimeColumns;
    }

    private static void updateColumnToEasternTime(Connection conn, String tableName, String column) throws SQLException {
        String selectQuery = "SELECT id, " + column + " FROM " + tableName;
        String updateQuery = "UPDATE " + tableName + " SET " + column + " = ? WHERE id = ?";

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");

        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(selectQuery);
             PreparedStatement pstmt = conn.prepareStatement(updateQuery)) {

            while (rs.next()) {
                int id = rs.getInt("id");
                LocalDateTime dateTime = rs.getTimestamp(column).toLocalDateTime();

                ZonedDateTime zonedDateTime = dateTime.atZone(ZoneId.of("UTC"));
                ZonedDateTime easternTime = zonedDateTime.withZoneSameInstant(ZoneId.of("America/New_York"));

                String formattedDateTime = easternTime.format(formatter);
                LocalDateTime parsedDateTime = LocalDateTime.parse(formattedDateTime, formatter);

                pstmt.setTimestamp(1, java.sql.Timestamp.valueOf(parsedDateTime));
                pstmt.setInt(2, id);
                pstmt.executeUpdate();
            }
        }
    }
}
