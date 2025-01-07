import org.springframework.stereotype.Service;

@Service
public class FileHandlerService {

    public void processFileHandlerRequest(String jsonRequest) {
        System.out.println("FileHandler JSON Request: " + jsonRequest);
        // Add logic for handling file-related operations if needed
    }
}
