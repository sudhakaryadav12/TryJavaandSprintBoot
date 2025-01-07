import org.springframework.stereotype.Service;

@Service
public class FISService {

    public void processFISRequest(String jsonRequest) {
        System.out.println("FIS JSON Request: " + jsonRequest);
        // Add logic for calling the vendor FIS if needed
    }
}
