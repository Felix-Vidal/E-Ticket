package br.ufac.eticketapi.service;

import java.util.List;

import org.springframework.stereotype.Service;

import br.ufac.eticketapi.model.TicketUnico;
import br.ufac.eticketapi.repository.TicketUnicoRepository;

@Service
public class TicketUnicoService implements IService<TicketUnico>{

    private TicketUnicoRepository repo;

    public TicketUnicoService(TicketUnicoRepository repo) {
        this.repo = repo;
    }

    @Override
    public List<TicketUnico> get() {
        return repo.findAll();
    }

    @Override
    public TicketUnico get(Long id) {
        return repo.findById(id).orElse(null);
    }

    @Override
    public List<TicketUnico> get(String termoBusca) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'get'");
    }

    @Override
    public TicketUnico save(TicketUnico objeto) {
        return repo.save(objeto);
    }

    @Override
    public void delete(Long id) {
        repo.deleteById(id);
    }

}
