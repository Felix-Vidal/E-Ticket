package br.ufac.eticketapi.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import br.ufac.eticketapi.model.EMetodoPagamento;
import br.ufac.eticketapi.model.TicketUnico;
import br.ufac.eticketapi.service.TicketUnicoService;

@RestController
@RequestMapping("/ticketunico")
public class TicketUnicoController implements IController<TicketUnico>{

    private TicketUnicoService servico;

    public TicketUnicoController(TicketUnicoService servico) {
        this.servico = servico;
    }

    @Override
    @GetMapping("/")
    public ResponseEntity<List<TicketUnico>> get() {
        List<TicketUnico> registros = servico.get();
        return new ResponseEntity<>(registros, HttpStatus.OK);
    }

    @Override
    @GetMapping("/{id}")
    public ResponseEntity<TicketUnico> get(@PathVariable("id") Long id) {
        TicketUnico registro = servico.get(id);
        return new ResponseEntity<>(registro, HttpStatus.OK);
    }

    @Override
    @GetMapping("/busca/{termoBusca}")
    public ResponseEntity<List<TicketUnico>> get(@PathVariable("termoBusca") String termoBusca) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'get'");
    }

    @GetMapping("/pagamento/{metodoPagamento}")
    public ResponseEntity<List<TicketUnico>> getMetodoPagamento(@PathVariable("termoBusca") EMetodoPagamento metodoPagamento){
        List<TicketUnico> registros = servico.getMetodoPagamento(metodoPagamento);
        return new ResponseEntity<>(registros, HttpStatus.OK);
    }

    @Override
    @PostMapping("/")
    public ResponseEntity<TicketUnico> insert(@RequestBody TicketUnico objeto) {
        TicketUnico registro = servico.save(objeto);
        return new ResponseEntity<>(registro, HttpStatus.CREATED);
    }

    @Override
    @PutMapping("/")
    public ResponseEntity<TicketUnico> update(@RequestBody TicketUnico objeto) {
        TicketUnico registro = servico.save(objeto);
        return new ResponseEntity<>(registro, HttpStatus.OK);
    }

    @Override
    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable("id") Long id) {
        servico.delete(id);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}
