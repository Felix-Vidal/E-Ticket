package br.ufac.eticketapi.service;

import java.util.List;

import org.springframework.stereotype.Service;

import br.ufac.eticketapi.model.Refeicao;
import br.ufac.eticketapi.repository.RefeicaoRepository;

@Service
public class RefeicaoService implements IService<Refeicao>{
    
    private RefeicaoRepository repo;

    public RefeicaoService(RefeicaoRepository repo) {
        this.repo = repo;
    }

    @Override
    public List<Refeicao> get() {
        return repo.findAll();
    }

    @Override
    public Refeicao get(Long id) {
        return repo.findById(id).orElse(null);
    }

    @Override
    public List<Refeicao> get(String termoBusca) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'get'");
    }

    @Override
    public Refeicao save(Refeicao objeto) {
        return repo.save(objeto);
    }

    @Override
    public void delete(Long id) {
        repo.deleteById(id);
    }
}
