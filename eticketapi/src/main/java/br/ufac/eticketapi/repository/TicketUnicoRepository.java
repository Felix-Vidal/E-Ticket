package br.ufac.eticketapi.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import br.ufac.eticketapi.model.EMetodoPagamento;
import br.ufac.eticketapi.model.TicketUnico;
import java.util.List;


public interface TicketUnicoRepository extends JpaRepository<TicketUnico, Long>{

    List<TicketUnico> findByMetodoPagamento(EMetodoPagamento metodoPagamento);
    
}
