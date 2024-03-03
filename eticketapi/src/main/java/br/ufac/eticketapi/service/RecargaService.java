package br.ufac.eticketapi.service;

import java.util.List;

import org.springframework.stereotype.Service;

import br.ufac.eticketapi.model.Recarga;
import br.ufac.eticketapi.model.Usuario;
import br.ufac.eticketapi.repository.RecargaRepository;

@Service
public class RecargaService implements IService<Recarga>{

    private final RecargaRepository repo;

    public RecargaService(RecargaRepository repo){
        this.repo = repo;
    }

    @Override
    public List<Recarga> get() {
        return repo.findAll();
    }

    @Override
    public Recarga get(Long id) {
        return repo.findById(id).orElse(null);
    }

    public List<Recarga> getUsuarioId(Long id) {
        return repo.findByUsuarioId(id);
    }    

    @Override
    public List<Recarga> get(String termoBusca) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'get'");
    }

    @Override
    public Recarga save(Recarga objeto) {
        return repo.save(objeto);
    }

    @Override
    public void delete(Long id) {
        repo.deleteById(id);
    }

    

}
