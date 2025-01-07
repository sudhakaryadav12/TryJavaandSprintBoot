
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.example.api.service.FISService;
import com.example.api.service.FileHandlerService;

@RestController
@RequestMapping("/api")
public class APIController {

    @Autowired
    private FISService fisService;

    @Autowired
    private FileHandlerService fileHandlerService;

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
