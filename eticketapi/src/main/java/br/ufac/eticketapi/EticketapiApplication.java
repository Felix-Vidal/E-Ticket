package br.ufac.eticketapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@SpringBootApplication
@Controller
public class EticketapiApplication {

	@RequestMapping("/")
	@ResponseBody
	public String exemplo() {
		return "E-Ticket Test";
	}
	public static void main(String[] args) {
		SpringApplication.run(EticketapiApplication.class, args);
	}

}
