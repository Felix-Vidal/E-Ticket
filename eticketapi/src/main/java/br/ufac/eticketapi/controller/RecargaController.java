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

import br.ufac.eticketapi.model.Recarga;
import br.ufac.eticketapi.model.Usuario;
import br.ufac.eticketapi.service.RecargaService;

@RestController
@RequestMapping("/recarga")
public class RecargaController implements IController<Recarga>{

    private RecargaService servico;

    public RecargaController(RecargaService servico){
        this.servico = servico;
    }

    @Override
    @GetMapping("/config/")
    public ResponseEntity<List<Recarga>> get() {
        List<Recarga> registros = servico.get();
        return new ResponseEntity<>(registros, HttpStatus.OK);
    }

    @Override
    @GetMapping("/{id}")
    public ResponseEntity<Recarga> get(@PathVariable("id") Long id) {
        Recarga registro = servico.get(id);
        return new ResponseEntity<>(registro, HttpStatus.OK);
    }

    @GetMapping("/usuario/{id}")
    public ResponseEntity<List<Recarga>> getUsuario(@PathVariable("id") Long id) {
        List<Recarga> registro = servico.getUsuarioId(id);
        return new ResponseEntity<>(registro, HttpStatus.OK);
    }

    @Override
    @GetMapping("/config/busca/{termoBusca}")
    public ResponseEntity<List<Recarga>> get(@PathVariable("termoBusca") String termoBusca) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'get'");
    }

    @Override
    @PostMapping("/")
    public ResponseEntity<Recarga> insert(@RequestBody Recarga objeto) {
        Recarga registro = servico.save(objeto);
        return new ResponseEntity<>(registro, HttpStatus.CREATED);
    }

    @Override
    @PutMapping("/")
    public ResponseEntity<Recarga> update(@RequestBody Recarga objeto) {
        Recarga registro = servico.save(objeto);
        return new ResponseEntity<>(registro, HttpStatus.OK);
    }

    @Override
    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable("id") Long id) {
        servico.delete(id);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}
