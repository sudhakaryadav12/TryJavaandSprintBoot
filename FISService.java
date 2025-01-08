import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.file.Path;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

@Service
public class FISService {

    public void processFISRequest(String jsonRequest) {
        System.out.println("FIS JSON Request: " + jsonRequest);
        // Add logic for calling the vendor FIS if needed
    }
    
    public void processFileAndJson(MultipartFile file, String json) {
        // Process the JSON data
        System.out.println("Received JSON: " + json);

        // Process the file
        try {
            StringBuilder fileContent = new StringBuilder();
            BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                fileContent.append(line).append("\n");
            }
            System.out.println("File Content: \n" + fileContent.toString());
            
            String filePath = "";
            
            // Step 1: Read JSON from the file in the folder
            Path path = Path.of(filePath);
            JsonObject fileJson;
            try (Reader freader = new FileReader(path.toFile())) {
                fileJson = JsonParser.parseReader(freader).getAsJsonObject();
            }
            System.out.println("JSON from file: " + fileJson);

            // Step 2: Parse JSON request
            JsonObject requestJson = JsonParser.parseString(json).getAsJsonObject();

            // Step 3: Set all key-values from requestJson to fileJson
            for (String key : requestJson.keySet()) {
                fileJson.add(key, requestJson.get(key));
            }

            // Step 4: Print the merged JSON
            System.out.println("Updated JSON: " + fileJson.toString());
        } catch (Exception e) {
            System.out.println("Error processing file: " + e.getMessage());
        }
    }
}
