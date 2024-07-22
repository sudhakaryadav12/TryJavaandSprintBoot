import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;

public class DateTimeUpdater {

    private JdbcTemplate jdbcTemplate;

    public DateTimeUpdater(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public void updateDateTimeToEasternTime(String tableName) {
        String easternTimeZone = "America/New_York";
        
        // Step 1: Get all datetime columns
        String sql = "SELECT column_name " +
                     "FROM information_schema.columns " +
                     "WHERE table_name = ? AND data_type = 'timestamp without time zone'";

        List<String> dateTimeColumns = jdbcTemplate.queryForList(sql, new Object[]{tableName}, String.class);

        // Step 2: Update each datetime column to Eastern Time
        for (String column : dateTimeColumns) {
            String updateSql = "UPDATE " + tableName + " SET " + column + " = ? WHERE " + column + " IS NOT NULL";

            List<Map<String, Object>> rows = jdbcTemplate.queryForList("SELECT id, " + column + " FROM " + tableName + " WHERE " + column + " IS NOT NULL");

            for (Map<String, Object> row : rows) {
                Timestamp originalTimestamp = (Timestamp) row.get(column);
                Timestamp easternTimestamp = convertToEasternTime(originalTimestamp, easternTimeZone);
                jdbcTemplate.update(updateSql, easternTimestamp, row.get("id"));
            }
        }
    }

    private Timestamp convertToEasternTime(Timestamp timestamp, String easternTimeZone) {
        TimeZone timeZone = TimeZone.getTimeZone(easternTimeZone);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        sdf.setTimeZone(timeZone);

        String easternTime = sdf.format(timestamp);
        return Timestamp.valueOf(easternTime);
    }

    public static void main(String[] args) {
        // Example usage
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName("org.postgresql.Driver");
        dataSource.setUrl("jdbc:postgresql://localhost:5432/your_database");
        dataSource.setUsername("your_username");
        dataSource.setPassword("your_password");

        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        DateTimeUpdater updater = new DateTimeUpdater(jdbcTemplate);

        updater.updateDateTimeToEasternTime("your_table_name");
    }
}
