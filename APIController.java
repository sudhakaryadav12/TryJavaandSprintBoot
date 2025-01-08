
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;


@RestController
@RequestMapping("/api")
public class APIController {

    @Autowired
    private FISService fisService;

    @Autowired
    private FileHandlerService fileHandlerService;
    
    @PostMapping(value = "/upload", consumes = {"multipart/form-data"})
    public ResponseEntity<String> uploadFileAndJson(
            @RequestPart("file") MultipartFile file,
            @RequestPart("data") String json) {
        try {
        	fisService.processFileAndJson(file, json);
            return ResponseEntity.ok("File and JSON processed successfully");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    // Endpoint for FIS API
    @PostMapping("/fis")
    public String callFIS(@RequestBody String jsonRequest) {
        fisService.processFISRequest(jsonRequest);
        return "FIS request processed";
    }

    // Endpoint for FileHandler API
    @PostMapping("/file-handler")
    public String callFileHandler(@RequestBody String jsonRequest) {
        fileHandlerService.processFileHandlerRequest(jsonRequest);
        return "FileHandler request processed";
    }
}
